from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app import qa_service

router = APIRouter()

@router.get("/status")
@router.get("/status/")
async def get_status() -> Dict[str, Any]:
    """
    Get the current status of the QA system
    """
    try:
        status_data = qa_service.get_system_status()
        # Ensure the status field is present for compatibility
        if "status" not in status_data:
            status_data["status"] = "ok"
        return status_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error getting system status") from e
