import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app import config
from app.models import FileUploadResponse, MultipleFileUploadResponse

router = APIRouter(prefix="/files", tags=["Files"])


def _ensure_upload_dir() -> None:
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)


def _resolve_safe_upload_path(filename: str) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Reject attempts to inject path separators or parent traversal.
    if os.path.basename(filename) != filename or filename in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid filename")

    upload_root = os.path.abspath(config.UPLOAD_DIR)
    candidate = os.path.abspath(os.path.join(config.UPLOAD_DIR, filename))

    try:
        if os.path.commonpath([upload_root, candidate]) != upload_root:
            raise HTTPException(status_code=400, detail="Invalid filename")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid filename") from exc

    return candidate


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file to the uploads directory."""
    try:
        _ensure_upload_dir()

        contents = await file.read()
        if len(contents) > config.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {config.MAX_UPLOAD_SIZE / (1024 * 1024):.1f}MB",
            )

        extension = os.path.splitext(file.filename or "")[1]
        unique_filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(config.UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as handle:
            handle.write(contents)

        return FileUploadResponse(
            status="success",
            message="File uploaded successfully",
            filename=unique_filename,
            original_filename=file.filename,
            size=len(contents),
            uploaded_at=datetime.now().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error uploading file") from exc


@router.post("/upload/multiple", response_model=MultipleFileUploadResponse)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files and report partial successes."""
    successful_uploads: List[FileUploadResponse] = []
    failed_uploads = []

    for upload in files:
        try:
            successful_uploads.append(await upload_file(upload))
        except HTTPException as exc:
            failed_uploads.append({"filename": upload.filename, "error": exc.detail})
        except Exception:
            failed_uploads.append({"filename": upload.filename, "error": "Upload failed"})

    return MultipleFileUploadResponse(
        status="success" if not failed_uploads else "partial_success",
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        total_files=len(files),
        successful_count=len(successful_uploads),
        failed_count=len(failed_uploads),
    )


@router.get("/list")
async def list_files(file_type: Optional[str] = Query(None, alias="type", description="Filter files by extension")):
    """List files currently stored in uploads."""
    try:
        _ensure_upload_dir()
        items = []

        for filename in os.listdir(config.UPLOAD_DIR):
            file_path = os.path.join(config.UPLOAD_DIR, filename)
            if not os.path.isfile(file_path):
                continue

            extension = os.path.splitext(filename)[1].lower()
            if file_type and file_type.lower() not in {"", "all"} and extension != f".{file_type.lower().lstrip('.')}":
                continue

            items.append(
                {
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                    "type": extension[1:] if extension else "",
                }
            )

        return {"status": "success", "files": items, "count": len(items)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error listing files") from exc


@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    """Delete a file from uploads by filename."""
    try:
        file_path = _resolve_safe_upload_path(filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        os.remove(file_path)
        return {"status": "success", "message": f"File {filename} deleted successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error deleting file") from exc
