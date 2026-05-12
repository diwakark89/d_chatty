# app/config.py - Configuration settings for the application
import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
RELOAD = os.getenv("RELOAD", "True").lower() in ("true", "1", "t")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

# Model settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sklearn-tfidf")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# File storage settings
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10 MB default
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 100000000))  # Default 100MB
ALLOWED_EXTENSIONS = [".pdf", ".txt", ".md"]

# API settings
API_PREFIX = os.getenv("API_PREFIX", "")
CORS_ORIGINS = [
	origin.strip()
	for origin in os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",")
	if origin.strip()
]

# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
