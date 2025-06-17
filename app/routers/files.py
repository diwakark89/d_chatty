import os
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.config import UPLOAD_DIR
from app.models import FileUploadResponse, MultipleFileUploadResponse

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/upload/multiple", response_model=MultipleFileUploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple files"""
    results = []
    for file in files:
        try:
            response = await upload_file(file)
            results.append(response)
        except Exception as e:
            # Log the error but continue with other files
            print(f"Error uploading {file.filename}: {e}")

    return MultipleFileUploadResponse(files=results)

@router.get("/list")
async def list_files():
    """List all files in the uploads directory"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Get list of files
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                files.append({
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                })

        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")
