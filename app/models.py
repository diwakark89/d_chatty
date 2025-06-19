from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class StatusResponse(BaseModel):
    pdf_uploaded: bool
    qa_chain_ready: bool
    embedding_model: str
    ollama_model: str
    timestamp: str

class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]

class FileUploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    original_filename: str
    size: int
    uploaded_at: str
    chunks_created: Optional[int] = None
    total_pages: Optional[int] = None




class MultipleFileUploadResponse(BaseModel):
    """Model for multiple file upload response"""
    files: List[FileUploadResponse]

class PDFUploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    chunks_created: int
    total_pages: int
    uploaded_at: str
