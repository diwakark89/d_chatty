from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class StatusResponse(BaseModel):
    pdf_uploaded: bool
    qa_chain_ready: bool
    embedding_model: str
    ollama_model: str
    timestamp: str

class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]

class QuestionResponse(BaseModel):
    status: str
    query: str
    answer: str
    source_documents: List[SourceDocument]
    timestamp: str
    model: Optional[str] = None

class FileUploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    original_filename: str
    size: int
    uploaded_at: str
    chunks_created: Optional[int] = None
    total_pages: Optional[int] = None
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SourceDocument(BaseModel):
    """Model for source document metadata"""
    content: str
    metadata: Dict[str, Any]

class StatusResponse(BaseModel):
    """Model for system status response"""
    pdf_uploaded: bool
    qa_chain_ready: bool
    embedding_model: str
    ollama_model: str
    timestamp: str

class QuestionResponse(BaseModel):
    """Model for question answer response"""
    status: str = "success"
    query: str
    answer: str
    model: Optional[str] = None
    source_documents: Optional[List[SourceDocument]] = None
    timestamp: str

class FileUploadResponse(BaseModel):
    """Model for file upload response"""
    status: str
    message: str
    filename: str
    original_filename: Optional[str] = None
    size: int
    uploaded_at: str

class MultipleFileUploadResponse(BaseModel):
    """Model for multiple file upload response"""
    files: List[FileUploadResponse]
class MultipleFileUploadResponse(BaseModel):
    files: List[FileUploadResponse]

class PDFUploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    chunks_created: int
    total_pages: int
    uploaded_at: str
