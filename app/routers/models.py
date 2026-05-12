import os
import requests
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query

from app import config
from app import qa_service

router = APIRouter(prefix="/models", tags=["Models"])

# Default models for fallback when Ollama is not available
DEFAULT_MODELS = [
    {
        "id": "mistral",
        "name": "Mistral 7B",
        "description": "Mistral 7B is a fast and accurate open-source LLM",
        "parameters": "7B",
        "is_default": True
    },
    {
        "id": "llama2",
        "name": "Llama 2",
        "description": "Meta's Llama 2 model",
        "parameters": "7B",
        "is_default": False
    },
    {
        "id": "phi3",
        "name": "Phi-3",
        "description": "Microsoft's Phi-3 model",
        "parameters": "3.8B", 
        "is_default": False
    }
]
@router.get("/list")
async def list_models():
    """
    List all available models from Ollama
    """
    try:
        # Try to get models from Ollama API
        try:
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "success",
                    "models": models,
                    "count": len(models)
                }
        except requests.RequestException as e:
            # If Ollama API request fails, log the error but continue to fallback
            print(f"Ollama API request failed: {e}")

        # Fallback to default models if Ollama API fails
        formatted_models = []
        for model in DEFAULT_MODELS:
            formatted_models.append({
                "name": model["id"],
                "modified_at": "",
                "size": 0
            })

        return {
            "status": "success",
            "models": formatted_models,
            "count": len(formatted_models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@router.get("/info/{model_name}")
async def get_model_info(model_name: str):
    """
    Get information about a specific model
    """
    try:
        # Try to get model info from Ollama API
        try:
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/show?name={model_name}", timeout=3)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "model": model_name,
                    "info": response.json()
                }
        except requests.RequestException as e:
            # If Ollama API request fails, log the error but continue to fallback
            print(f"Ollama API request failed: {e}")

        # Fallback to default models if Ollama API fails
        for model in DEFAULT_MODELS:
            if model["id"] == model_name:
                return {
                    "status": "success",
                    "model": model_name,
                    "info": model
                }

        # If we reach here, the model was not found
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing model: {str(e)}")
