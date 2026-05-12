# DChatty

DChatty is a FastAPI-based PDF question-answering service that indexes uploaded PDFs and answers questions using an Ollama-backed RetrievalQA pipeline.

## Features

- Upload PDF documents and index them for retrieval
- Ask natural-language questions against uploaded content
- View source snippets used in answers
- Switch Ollama models through API/UI
- Persist vector-store state across restarts (compressed + backup recovery)

## Tech Stack

- Python 3.11
- FastAPI + Uvicorn
- LangChain + Ollama
- FAISS + scikit-learn TF-IDF embeddings
- Docker Compose for local multi-service runs

## Quick Start (Local)

1. Create and activate virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Create configuration file.

```powershell
Copy-Item .env.example .env
```

4. Start the API.

```powershell
.\.venv\Scripts\python.exe run.py
```

## Quick Start (Docker)

1. Ensure `.env` exists (copy from `.env.example`).
2. Start services.

```powershell
docker compose up -d --build
```

3. Stop services.

```powershell
docker compose down
```

## Endpoints

Base API prefix: `/api/v1`

- `POST /api/v1/pdf/upload` - Upload and process a PDF
- `GET /api/v1/pdf/ask?query=...&model=...` - Ask a question
- `GET /api/v1/files/list` - List uploaded files
- `DELETE /api/v1/files/delete/{filename}` - Delete uploaded file
- `GET /api/v1/models/list` - List Ollama models (returns 503 if Ollama unavailable)
- `GET /api/v1/models/info/{model_name}` - Model metadata
- `POST /api/v1/models/change?model_name=...` - Switch active QA model
- `GET /status` - Service status

## UI and Docs

- Web UI: http://127.0.0.1:8000/static/index.html
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Configuration

Use `.env` (template: `.env.example`). Main variables:

- `HOST`, `PORT`, `RELOAD`, `DEBUG`
- `UPLOAD_DIR`, `MAX_UPLOAD_SIZE`, `MAX_FILE_SIZE`
- `CORS_ORIGINS`
- `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `EMBEDDING_MODEL`
- `DATABASE_URL` (optional, currently not required by core app flow)

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Notes

- Use the project virtual environment (`.venv`) for reliable execution.
- Persistence files are stored in `data/` and backups in `data/backups/`.
- Docker Compose credentials in `.env.example` are development placeholders and must be changed for real deployments.
