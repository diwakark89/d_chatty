import os
import uuid
import tempfile
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from datetime import datetime
from app.config import UPLOAD_DIR

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_file(file: UploadFile) -> Dict[str, Any]:
    """Save a file to disk and return file information"""
    try:
        # Generate a unique filename to prevent overwrites
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_location = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the file
        with open(file_location, "wb") as file_object:
            file_object.write(await file.read())

        return {
            "status": "success",
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "original_filename": file.filename,
            "size": os.path.getsize(file_location),
            "uploaded_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


async def save_multiple_files(files: List[UploadFile]) -> List[Dict[str, Any]]:
    """Save multiple files to disk and return file information"""
    results = []
    for file in files:
        try:
            result = await save_file(file)
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "original_filename": file.filename,
                "message": f"Error uploading file: {str(e)}"
            })

    return results


async def create_temp_file(file: UploadFile) -> str:
    """Create a temporary file from an uploaded file

    Args:
        file: The uploaded file

    Returns:
        Path to the temporary file
    """
    # Validate file type for PDF endpoints
    if file.filename and file.filename.lower().endswith('.pdf'):
        suffix = '.pdf'
    else:
        suffix = os.path.splitext(file.filename)[1] if file.filename else ''

    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            return temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating temporary file: {str(e)}")


def delete_temp_file(file_path: str) -> None:
    """Delete a temporary file

    Args:
        file_path: Path to the temporary file
    """
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary file {file_path}: {e}")
