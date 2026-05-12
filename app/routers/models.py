import logging
import requests
from fastapi import APIRouter, HTTPException, Query

from app import config
from app import qa_service

router = APIRouter(prefix="/models", tags=["Models"])
logger = logging.getLogger(__name__)


def _raise_ollama_unavailable(exc: Exception) -> None:
    logger.warning("Ollama is unavailable: %s", exc)
    raise HTTPException(status_code=503, detail="Ollama service is unavailable") from exc


@router.get("/list")
async def list_models():
    """
    List all available models from Ollama
    """
    try:
        try:
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=3)
        except requests.RequestException as exc:
            _raise_ollama_unavailable(exc)

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Ollama service is unavailable")

        models = response.json().get("models", [])
        return {"status": "success", "models": models, "count": len(models)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error listing models") from exc

@router.get("/info/{model_name}")
async def get_model_info(model_name: str):
    """
    Get information about a specific model
    """
    try:
        try:
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/show?name={model_name}", timeout=3)
        except requests.RequestException as exc:
            _raise_ollama_unavailable(exc)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Ollama service is unavailable")

        return {
            "status": "success",
            "model": model_name,
            "info": response.json(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error getting model info") from exc

@router.post("/change")
async def change_model(model_name: str = Query(..., description="Name of the model to use")):
    """
    Change the active model for QA
    """
    try:
        # Initialize QA chain with the new model
        qa_service.initialize_qa_chain(model_name=model_name)

        return {
            "status": "success",
            "message": f"Model changed to {model_name}",
            "model": model_name
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error changing model") from exc
