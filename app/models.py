from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]

class StatusResponse(BaseModel):
    """System status response model"""
    status: str = Field(..., description="Status of the system")
    timestamp: str = Field(..., description="Current timestamp")
    vector_store: Optional[Dict[str, Any]] = Field(None, description="Vector store statistics")
    cache: Optional[Dict[str, Any]] = Field(None, description="Cache statistics")
    memory: Optional[Dict[str, float]] = Field(None, description="Memory usage statistics")
    uptime_seconds: Optional[float] = Field(None, description="System uptime in seconds")
    pdf_uploaded: Optional[bool] = Field(None, description="Whether a PDF has been uploaded")
    qa_chain_ready: Optional[bool] = Field(None, description="Whether the QA chain is ready")
    embedding_model: Optional[str] = Field(None, description="Name of the embedding model")
    ollama_model: Optional[str] = Field(None, description="Name of the Ollama model")


class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    status: str = Field(..., description="Status of the upload")
    message: str = Field(..., description="Status message")
    filename: str = Field(..., description="Name of the uploaded file")
    original_filename: Optional[str] = Field(None, description="Original name of the uploaded file")
    chunks_created: Optional[int] = Field(None, description="Number of chunks created from the document")
    total_pages: Optional[int] = Field(None, description="Total number of pages in the document")
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    uploaded_at: str = Field(..., description="Timestamp of upload")


class MultipleFileUploadResponse(BaseModel):
    """Response model for multiple file uploads"""
    status: str = Field(..., description="Overall status of the uploads")
    successful_uploads: List[FileUploadResponse] = Field([], description="Successfully uploaded files")
    failed_uploads: List[Dict[str, Any]] = Field([], description="Failed uploads with errors")
    total_files: int = Field(..., description="Total number of files processed")
    successful_count: int = Field(..., description="Number of successful uploads")
    failed_count: int = Field(..., description="Number of failed uploads")


class QuestionAnswerResponse(BaseModel):
    """Response model for question answering"""
    status: str = Field(..., description="Status of the query")
    query: str = Field(..., description="Original query")
    model: Optional[str] = Field(None, description="Model used for answering")
    answer: str = Field(..., description="Generated answer")
    source_documents: List[Dict[str, Any]] = Field(..., description="Source documents used for the answer")
    timestamp: str = Field(..., description="Timestamp of the query")
