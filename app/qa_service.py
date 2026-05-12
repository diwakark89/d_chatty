import logging
import os
import threading
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

import numpy as np
from fastapi import HTTPException
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
# Use scikit-learn embeddings instead of sentence-transformers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from app.config import OLLAMA_MODEL, OLLAMA_BASE_URL

logger = logging.getLogger(__name__)

class SimpleSklearnEmbeddings:
    def __init__(self, max_features=10000, min_df=2, max_df=0.85):
        # Optimize memory usage by limiting vocabulary size and filtering rare terms
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,  # Limit vocabulary size
            min_df=min_df,              # Ignore terms that appear in fewer than min_df documents
            max_df=max_df,              # Ignore terms that appear in more than max_df proportion of documents
            lowercase=True,             # Convert to lowercase for better matching
            norm='l2',                  # Apply L2 normalization
            sublinear_tf=True           # Apply sublinear tf scaling (1 + log(tf))
        )
        self.fitted = False
        self.vector_size = max_features  # Initial default size
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initialized optimized SimpleSklearnEmbeddings")

    def embed_documents(self, texts):
        self.logger.debug(f"Embedding {len(texts)} documents")
        if not self.fitted:
            self.logger.info("Fitting vectorizer on documents")
            self.vectorizer.fit(texts)
            self.fitted = True
            # Update vector size based on actual vocabulary
            self.vector_size = len(self.vectorizer.get_feature_names_out())
            self.logger.info(f"Vocabulary size: {self.vector_size}")

        # Use sparse matrices instead of dense arrays to reduce memory usage
        vectors = self.vectorizer.transform(texts)
        # Only normalize but don't convert to dense array unless needed
        normalized = normalize(vectors, norm='l2', copy=False)
        self.logger.debug(f"Embedded documents shape: {normalized.shape}")

        # FAISS requires dense arrays, so we need to convert
        # But we'll let the caller decide whether to convert to dense
        # to avoid unnecessary memory usage
        return normalized

    def embed_query(self, text):
        self.logger.debug(f"Embedding query: {text[:30]}...")
        if not self.fitted:
            self.logger.warning("Vectorizer not fitted, returning zero vector")
            return np.zeros(self.vector_size)

        # Use sparse matrices for efficiency
        vector = self.vectorizer.transform([text])
        normalized = normalize(vector, norm='l2', copy=False)
        # Only convert to array for the final result
        result = normalized[0].toarray()[0]
        self.logger.debug(f"Query vector shape: {result.shape}")
        return result

    def __call__(self, text):
        """Make the embeddings callable to support Langchain's interfaces"""
        if isinstance(text, list):
            return self.embed_documents(text)
        else:
            return self.embed_query(text)


# Configuration constants
MAX_CACHE_SIZE = 50  # Maximum number of queries to cache

# Create optimized embedding instance
embeddings = SimpleSklearnEmbeddings(max_features=10000, min_df=2, max_df=0.85)
logger.info("Initialized optimized TF-IDF embeddings")

# Global variables for vector store and QA chain
vector_store: Optional[FAISS] = None
qa_chain: Optional[RetrievalQA] = None
state_lock = threading.RLock()

# Try to load saved state at module initialization
try:
    from app import persistence
    logger.info("Checking for saved state...")
    saved_state = persistence.load_qa_state()
    if saved_state and "vector_store" in saved_state:
        logger.info("Found saved QA state, restoring...")
        with state_lock:
            vector_store = saved_state["vector_store"]
        logger.info(f"Restored vector store with {vector_store.index.ntotal} vectors")
        logger.info("State loaded successfully")
except Exception as e:
    logger.error(f"Failed to load saved state: {e}")


# Cache for LLM models to avoid recreating them
llm_cache = {}

# Simple query cache
query_cache = {}


def _build_cache_key(query: str, model_name: Optional[str]) -> Tuple[str, str]:
    return (model_name or OLLAMA_MODEL, query)

# Import get_answer utility
from app.get_answer import get_answer as get_answer_impl

def initialize_qa_chain(model_name=None):
    """Initialize the QA chain with Ollama model

    Args:
        model_name: Optional model name to use. If None, uses the default from config.
    """
    global qa_chain, vector_store, llm_cache

    try:
        with state_lock:
            if vector_store is None:
                raise HTTPException(status_code=400, detail="No PDF has been uploaded yet. Please upload a PDF first.")

            # Use the specified model or fall back to the default
            model_to_use = model_name or OLLAMA_MODEL
            logger.info(f"Initializing QA chain with model: {model_to_use}")

            # Check if we already have this model in cache
            if model_to_use in llm_cache:
                logger.info(f"Using cached LLM for model: {model_to_use}")
                llm = llm_cache[model_to_use]
            else:
                # Create new LLM and cache it
                logger.info(f"Creating new LLM instance for model: {model_to_use}")
                llm = Ollama(model=model_to_use, base_url=OLLAMA_BASE_URL)
                llm_cache[model_to_use] = llm

            # Configure optimized retriever with higher k for better recall
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 5,  # Retrieve more documents for better context
                    "fetch_k": 10  # Consider more candidates before filtering to k
                }
            )

            # Create QA chain with optimized parameters
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",  # Simple document concatenation
                retriever=retriever,
                return_source_documents=True,
                verbose=False
            )

            logger.info("QA chain initialized successfully")
            return qa_chain
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initialize QA chain: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize QA chain") from e


def get_answer(query: str, model_name: Optional[str] = None) -> Dict[str, Any]:
    """Get an answer for a question using the QA chain

    Args:
        query: The question to ask
        model_name: Optional model name to use for this question

    Returns:
        Dict containing answer and source documents
    """
    cache_key = _build_cache_key(query, model_name)
    with state_lock:
        if cache_key in query_cache:
            logger.info(f"Using cached answer for query: {query}")
            return query_cache[cache_key]

        current_qa_chain = qa_chain
        current_vector_store = vector_store

    # Use the implementation from get_answer.py
    response = get_answer_impl(current_qa_chain, current_vector_store, query, model_name, initialize_qa_chain)

    with state_lock:
        query_cache[cache_key] = response

        # Maintain cache size
        if len(query_cache) > MAX_CACHE_SIZE:
            oldest_key = next(iter(query_cache))
            del query_cache[oldest_key]

    return response


def process_pdf(file_path: str) -> Dict[str, Any]:
    """Process a PDF file and prepare it for QA"""
    global vector_store, qa_chain

    try:
        # Start timing for performance monitoring
        start_time = datetime.now()
        logger.info(f"Starting PDF processing: {file_path}")

        # First, check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"File not found: {file_path}")

        # Load and process the PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        if not documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

        # Use RecursiveCharacterTextSplitter for better chunk quality
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks could be created from the PDF")

        # Add timestamp and source metadata to chunks
        processed_at = datetime.now().isoformat()
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": i,
                "total_chunks": len(chunks),
                "source_file": file_path,
                "processed_at": processed_at
            })

        # Create FAISS vector store with multiple fallback methods
        logger.info(f"Creating vector store with {len(chunks)} chunks")

        # Extract text and metadata separately to avoid potential object reference issues
        texts = [doc.page_content for doc in chunks]
        metadatas = [doc.metadata for doc in chunks]

        # First try the standard method
        success = False
        new_vector_store = None
        try:
            new_vector_store = FAISS.from_documents(chunks, embeddings)
            success = True
            logger.info("Successfully created vector store using standard method")
        except Exception as e:
            logger.warning(f"Error creating vector store directly: {e}")

        # Second fallback: Try with manual embedding and standard FAISS constructor
        if not success:
            try:
                logger.info("Trying first fallback method with manual embedding")
                new_vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
                success = True
                logger.info("Successfully created vector store using first fallback method")
            except Exception as e:
                logger.warning(f"Error with first fallback method: {e}")

        # Third fallback: Try with very simplified approach and fewer chunks
        if not success:
            try:
                logger.info("Trying second fallback method with reduced data")
                # Take only the first 50 chunks to reduce complexity
                reduced_texts = texts[:min(50, len(texts))]
                reduced_metadatas = metadatas[:min(50, len(metadatas))]

                # Use the most basic FAISS setup
                new_vector_store = FAISS.from_texts(reduced_texts, embeddings, metadatas=reduced_metadatas)
                success = True
                logger.warning("Created vector store with reduced data (only first 50 chunks)")
            except Exception as e:
                logger.error(f"All fallback methods failed: {e}")
                raise HTTPException(status_code=500, detail="Failed to create vector store after multiple attempts")

        with state_lock:
            vector_store = new_vector_store
            qa_chain = None

        # Initialize QA chain
        initialize_qa_chain()

        # Save the state for persistence across restarts
        try:
            from app import persistence
            with state_lock:
                persisted_vector_store = vector_store
            state = {
                "vector_store": persisted_vector_store,
                "total_pages": len(documents),
                "chunks_created": len(chunks),
                "timestamp": datetime.now().isoformat()
            }
            persistence.save_qa_state(state)
            logger.info("Saved state to persistence storage")
        except Exception as e:
            logger.error(f"Failed to save persistence state: {e}")

        # Log performance metrics
        processing_time = datetime.now() - start_time
        logger.info(f"PDF processing completed in {processing_time.total_seconds():.2f} seconds")

        return {
            "chunks_created": len(chunks),
            "total_pages": len(documents),
            "processing_time_seconds": processing_time.total_seconds()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Error processing PDF") from e


def get_system_status() -> Dict[str, Any]:
    """Get the current status of the QA system with detailed metrics"""
    global vector_store, qa_chain, llm_cache, query_cache

    with state_lock:
        current_vector_store = vector_store
        current_qa_chain = qa_chain
        cached_models = list(llm_cache.keys())
        cache_size = len(query_cache)

    status = {
        "status": "ok",  # Add the required status field
        "pdf_uploaded": current_vector_store is not None,
        "qa_chain_ready": current_qa_chain is not None,
        "embedding_model": "sklearn-tfidf-optimized",
        "ollama_model": OLLAMA_MODEL,
        "ollama_base_url": OLLAMA_BASE_URL,
        "timestamp": datetime.now().isoformat()
    }

    # Add vector store stats if available
    if current_vector_store is not None:
        try:
            # Get index stats from FAISS
            index_stats = {
                "vector_count": current_vector_store.index.ntotal,
                "vector_dimension": current_vector_store.index.d
            }
            status["vector_store"] = index_stats
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            status["vector_store"] = {"error": str(e)}

    # Add cache stats
    status["cache"] = {
        "llm_models_cached": cached_models,
        "query_cache_size": cache_size,
        "query_cache_max_size": MAX_CACHE_SIZE
    }

    # Add memory usage if psutil is available
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        status["memory"] = {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "vms_mb": memory_info.vms / (1024 * 1024)
        }
    except ImportError:
        pass

    return status
