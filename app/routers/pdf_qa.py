import os
import tempfile
from datetime import datetime

from fastapi import APIRouter, File, UploadFile
from fastapi import Query, HTTPException

from app import qa_service
from app.config import MAX_UPLOAD_SIZE
from app.models import QuestionAnswerResponse, StatusResponse

router = APIRouter(prefix="/pdf", tags=["PDF QA"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for processing
    """
    # Check file size limit
    if file.size and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE/(1024*1024)}MB")

    # Check file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Read the file in chunks to handle large files
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Process the PDF in qa_service
        result = qa_service.process_pdf(temp_path)

        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except Exception as e:
            # Just log this error, don't fail the whole request
            print(f"Warning: Failed to delete temporary file {temp_path}: {e}")

        # Return success response
        return {
            "status": "success",
            "message": "PDF processed successfully",
            "filename": file.filename,
            **result
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.get("/ask", response_model=QuestionAnswerResponse)
async def ask_question(
    query: str = Query(..., description="Question to ask about the uploaded PDF"),
    model: str = Query(None, description="Optional model name to use for this question")
):
    """
    Ask questions about the uploaded PDF
    """
    try:
        result = qa_service.get_answer(query, model_name=model)

        return QuestionAnswerResponse(
            status="success",
            query=query,
            model=model,
            answer=result["answer"],
            source_documents=result["source_documents"],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
