import os
import uuid
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import our custom modules
from app import config
from app.config import DEBUG
from app.models import (
    StatusResponse,
    FileUploadResponse,
    MultipleFileUploadResponse
)

# Create FastAPI app
app = FastAPI(
    title="PDF QA API",
    description="API for PDF processing and question answering",
    version="0.1.0",
    debug=DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory if it exists
if os.path.exists('static'):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
from app.routers import pdf_qa, files, models
app.include_router(pdf_qa.router)
app.include_router(files.router)
app.include_router(models.router)

# Root endpoint
@app.get("/")
async def read_root():
    return {"status": "ok", "message": "PDF QA API is running"}

# Status endpoint - this will be overridden by the one in pdf_qa.router
# but we keep it here as a fallback
@app.get("/status/")
async def get_status():
    return StatusResponse(
        pdf_uploaded=False,
        qa_chain_ready=False,
        embedding_model=config.EMBEDDING_MODEL,
        ollama_model=config.OLLAMA_MODEL,
        timestamp=datetime.now().isoformat()
    )

# File upload endpoint as a fallback
@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    # Create uploads directory if it doesn't exist
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(config.UPLOAD_DIR, unique_filename)

    # Save the file
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    # Return the response
    return FileUploadResponse(
        status="success",
        message="File uploaded successfully",
        filename=unique_filename,
        original_filename=file.filename,
        size=len(contents),
        uploaded_at=datetime.now().isoformat()
    )

# Multiple file upload endpoint
@app.post("/api/upload/multiple", response_model=MultipleFileUploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    result = []
    for file in files:
        response = await upload_file(file)
        result.append(response.dict())

    return MultipleFileUploadResponse(files=result)
