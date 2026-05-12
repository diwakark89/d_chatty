import os
import tempfile
from datetime import datetime
import logging

from fastapi import APIRouter, File, UploadFile
from fastapi import Query, HTTPException

from app import qa_service
from app.config import MAX_UPLOAD_SIZE
from app.models import QuestionAnswerResponse

router = APIRouter(prefix="/pdf", tags=["PDF QA"])
logger = logging.getLogger(__name__)


def _looks_like_pdf(signature_bytes: bytes) -> bool:
    """Validate PDF signature in the first kilobyte."""
    if not signature_bytes:
        return False
    return b"%PDF" in signature_bytes[:1024]


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for processing
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    if file.size and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE / (1024 * 1024):.1f}MB",
        )

    temp_path = None

    try:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            total_size = 0
            header_bytes = b""
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break

                if len(header_bytes) < 1024:
                    header_bytes += chunk[: 1024 - len(header_bytes)]

                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE / (1024 * 1024):.1f}MB",
                    )

                temp_file.write(chunk)

            temp_path = temp_file.name

        if total_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        if not _looks_like_pdf(header_bytes):
            raise HTTPException(status_code=400, detail="Uploaded file content is not a valid PDF")

        # Process the PDF in qa_service
        result = qa_service.process_pdf(temp_path)

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
    except Exception as exc:
        # Handle any other errors
        raise HTTPException(status_code=500, detail="Error processing PDF") from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as exc:
                logger.warning("Failed to delete temporary file %s: %s", temp_path, exc)


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
            model=result.get("model"),
            answer=result["answer"],
            source_documents=result["source_documents"],
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error processing question") from exc
