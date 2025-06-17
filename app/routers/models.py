from fastapi import APIRouter, HTTPException
import requests
from typing import Dict, List, Any
import os

router = APIRouter(prefix="/models", tags=["Models"])

# Ollama API URL (default to localhost but allow override via env var)
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")

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

@router.get("/")
async def get_models() -> Dict[str, Any]:
    """
    Get available models from Ollama
    """
    try:
        # Try to connect to Ollama API
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        response.raise_for_status()
        # Return the models list
        return response.json()
    except requests.RequestException as e:
        # If we can't connect to Ollama, return a default list
        return {
            "models": [
                {"name": "phi3", "modified_at": "", "size": 0},
                {"name": "mistral", "modified_at": "", "size": 0},
                {"name": "llama3", "modified_at": "", "size": 0}
            ]
        }

@router.get("/list")
async def list_models():
    """List all available models"""
    try:
        # In a real implementation, you might query Ollama for available models
        # For now, return default models
        return {
            "models": DEFAULT_MODELS
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@router.get("/info/{model_id}")
async def get_model_info(model_id: str):
    """Get detailed information about a specific model"""
    try:
        # Find the model in our list
        for model in DEFAULT_MODELS:
            if model["id"] == model_id:
                return model

        # If we get here, model wasn't found
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

@router.get("/details/{model_name}")
async def get_model_details(model_name: str) -> Dict[str, Any]:
    """
    Get details for a specific model
    """
    try:
        # Try to connect to Ollama API
        response = requests.get(f"{OLLAMA_API_URL}/api/show?name={model_name}", timeout=5)
        response.raise_for_status()

        # Return the model details
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama API: {str(e)}")
