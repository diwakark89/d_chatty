from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from datetime import datetime
from app import qa_service, file_service

router = APIRouter(prefix="", tags=["PDF QA"])

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF file and process it for QA
    """
    temp_file_path = None
    try:
        # Create temporary file
        temp_file_path = await file_service.create_temp_file(file)

        # Process the PDF
        result = qa_service.process_pdf(temp_file_path)

        return {
            "status": "success",
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
            "chunks_created": result["chunks_created"],
            "total_pages": result["total_pages"],
            "uploaded_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_file_path:
            file_service.delete_temp_file(temp_file_path)

@router.get("/ask/")
async def ask_question(
    query: str = Query(..., description="Question to ask about the uploaded PDF"),
    model: str = Query(None, description="Optional model name to use for this question")
):
    """
    Endpoint to ask questions about the uploaded PDF
    """
    result = qa_service.get_answer(query, model_name=model)

    return {
        "status": "success",
        "query": query,
        "model": model,
        "answer": result["answer"],
        "source_documents": result["source_documents"],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/status/")
async def get_status():
    """
    Get the current status of the QA system
    """
    status = qa_service.get_system_status()
    status["timestamp"] = datetime.now().isoformat()

    return status
