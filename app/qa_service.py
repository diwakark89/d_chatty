from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from app.config import EMBEDDING_MODEL, OLLAMA_MODEL

# Use scikit-learn embeddings instead of sentence-transformers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# Create a simple embedding model using scikit-learn
vectorizer = TfidfVectorizer()


class SimpleSklearnEmbeddings:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.fitted = False
        self.vector_size = 100  # Default vector size
        print("Initialized SimpleSklearnEmbeddings")

    def embed_documents(self, texts):
        print(f"Embedding {len(texts)} documents")
        if not self.fitted:
            print("Fitting vectorizer on documents")
            self.vectorizer.fit(texts)
            self.fitted = True
            # Update vector size based on actual vocabulary
            self.vector_size = len(self.vectorizer.get_feature_names_out())
            print(f"Vocabulary size: {self.vector_size}")
        vectors = self.vectorizer.transform(texts).toarray()
        normalized = normalize(vectors)
        print(f"Embedded documents shape: {normalized.shape}")
        return normalized

    def embed_query(self, text):
        print(f"Embedding query: {text[:30]}...")
        if not self.fitted:
            # If not fitted, just return a zero vector
            print("Warning: Vectorizer not fitted, returning zero vector")
            return [0.0] * self.vector_size
        vector = self.vectorizer.transform([text]).toarray()
        normalized = normalize(vector)[0]
        print(f"Query vector shape: {normalized.shape}")
        return normalized

    def __call__(self, text):
        """Make the embeddings callable to support Langchain's interfaces"""
        print(f"__call__ received: {type(text)}")
        if isinstance(text, list):
            print("Calling embed_documents from __call__")
            return self.embed_documents(text)
        else:
            print("Calling embed_query from __call__")
            return self.embed_query(text)


# Create embedding instance
embeddings = SimpleSklearnEmbeddings()
print("Using SimpleSklearnEmbeddings as fallback - basic functionality enabled")

# Global variables for vector store and QA chain
vector_store: Optional[FAISS] = None
qa_chain: Optional[RetrievalQA] = None


def initialize_qa_chain(model_name=None):
    """Initialize the QA chain with Ollama model

    Args:
        model_name: Optional model name to use. If None, uses the default from config.
    """
    global qa_chain, vector_store

    if vector_store is None:
        raise HTTPException(status_code=400, detail="No PDF has been uploaded yet. Please upload a PDF first.")

    try:
        # Use the specified model or fall back to the default
        model_to_use = model_name or OLLAMA_MODEL
        print(f"Initializing QA chain with model: {model_to_use}")

        llm = Ollama(model=model_to_use)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize QA chain: {str(e)}")


def process_pdf(file_path: str) -> Dict[str, Any]:
    """Process a PDF file and prepare it for QA"""
    global vector_store, qa_chain

    try:
        # Load and process the PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        if not documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

        # Split text into chunks
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(documents)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks could be created from the PDF")

        # Create FAISS vector store - make sure to handle our custom embeddings properly
        try:
            vector_store = FAISS.from_documents(chunks, embeddings)
            print(f"Successfully created vector store with {len(chunks)} chunks")
        except Exception as e:
            print(f"Error creating vector store: {e}")
            # Fallback - create vectors manually and then initialize FAISS
            document_embeddings = embeddings.embed_documents([doc.page_content for doc in chunks])
            vector_store = FAISS.from_embeddings(
                text_embeddings=document_embeddings,
                metadatas=[doc.metadata for doc in chunks],
                texts=[doc.page_content for doc in chunks],
                embedding=embeddings
            )

        # Initialize QA chain
        initialize_qa_chain()

        return {
            "chunks_created": len(chunks),
            "total_pages": len(documents)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

def get_answer(query: str, model_name=None) -> Dict[str, Any]:
    """Get an answer for a query about the uploaded PDF

    Args:
        query: The question to ask
        model_name: Optional model name to use for this question
    """
    global qa_chain, vector_store

    try:
        # Check if we have a vector store
        if vector_store is None:
            raise HTTPException(status_code=400, detail="No PDF has been uploaded yet. Please upload a PDF first.")

        # Check if we need to initialize or reinitialize the QA chain with a different model
        if qa_chain is None or (model_name is not None and model_name != OLLAMA_MODEL):
            initialize_qa_chain(model_name)

        # Execute the query
        result = qa_chain({"query": query})

        # Extract and format the answer
        answer = result.get("result", "No answer found")

        # Extract source documents
        source_docs = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                source_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

        return {
            "answer": answer,
            "source_documents": source_docs
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error getting answer: {str(e)}")



def get_system_status() -> Dict[str, Any]:
    """Get the current status of the QA system"""
    return {
        "pdf_uploaded": vector_store is not None,
        "qa_chain_ready": qa_chain is not None,
        "embedding_model": "sklearn-tfidf",  # Custom embedding model name
        "ollama_model": OLLAMA_MODEL
    }
