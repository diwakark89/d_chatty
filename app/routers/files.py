import os
import os
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, File, UploadFile, Query

from app import config
from app.models import FileUploadResponse, MultipleFileUploadResponse

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a general file to the system
    """
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/upload/multiple", response_model=MultipleFileUploadResponse)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files to the system
    """
    successful = []
    failed = []

    for file in files:
        try:
            response = await upload_file(file)
            successful.append(response)
        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })

    return MultipleFileUploadResponse(
        status="success" if len(failed) == 0 else "partial_success",
        successful_uploads=successful,
        failed_uploads=failed,
        total_files=len(files),
        successful_count=len(successful),
        failed_count=len(failed)
    )

@router.get("/list")
async def list_files(type: str = Query(None, description="Filter files by type")):
    """
    List all uploaded files
    """
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)

        # List all files in the uploads directory
        files = []
        for filename in os.listdir(config.UPLOAD_DIR):
            file_path = os.path.join(config.UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                file_extension = os.path.splitext(filename)[1].lower()
                # Filter by type if specified
                if type is None or (type.lower() in ["", "all"]) or file_extension.startswith(f".{type.lower()}"):
                    files.append({
                        "filename": filename,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        "type": file_extension[1:] if file_extension else ""
                    })

        return {
            "status": "success",
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    """
    Delete a file from the system
    """
    try:
        file_path = os.path.join(config.UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        os.remove(file_path)

        return {
            "status": "success",
            "message": f"File {filename} deleted successfully"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
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
