import logging
from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_answer(qa_chain, vector_store, query: str, model_name: Optional[str] = None, 
               initialize_func: Optional[Callable] = None) -> Dict[str, Any]:
    """Implementation of getting an answer from the QA chain

    Args:
        qa_chain: The QA chain to use
        vector_store: The vector store containing document embeddings
        query: The question to ask
        model_name: Optional model name to use for this question
        initialize_func: Function to initialize the QA chain if needed

    Returns:
        Dict containing answer and source documents
    """
    # Validate input
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Check if we have a vector store
        if vector_store is None:
            raise HTTPException(status_code=400, detail="No PDF has been uploaded yet. Please upload a PDF first.")

        # Check if we need to initialize the QA chain with a specific model
        if qa_chain is None or (model_name is not None):
            if initialize_func:
                qa_chain = initialize_func(model_name)
            else:
                raise HTTPException(status_code=500, detail="QA chain initialization function not provided")

        # Execute the query
        logger.info(f"Querying with: {query[:50]}...")
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
            "source_documents": source_docs,
            "model": model_name,
            "query": query
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting answer: {e}")
        raise HTTPException(status_code=500, detail="Error processing question") from e
