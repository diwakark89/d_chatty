# AGENTS.md

## Project Overview

DChatty is a FastAPI-based PDF Question Answering API and web UI. Users upload PDF files, the backend indexes document chunks into FAISS, and questions are answered through an Ollama-backed RetrievalQA pipeline.

Primary stack:
- Python 3.11
- FastAPI + Uvicorn
- LangChain + Ollama
- FAISS + scikit-learn TF-IDF embeddings
- Docker Compose for local multi-service deployment

## Architecture Notes

Core code layout:
- `app/main.py`: FastAPI app creation, middleware, router registration
- `app/routers/`: API surface (`pdf_qa.py`, `files.py`, `models.py`, `status.py`, `ui.py`)
- `app/qa_service.py`: PDF processing, vector store construction, QA chain init, answer retrieval
- `app/persistence.py`: state persistence and restore
- `app/config.py`: env-driven settings and defaults
- `static/`: frontend assets
- `uploads/`: uploaded files in local runs

Data flow (upload to answer):
1. Upload PDF via `/api/v1/pdf/upload`.
2. `qa_service.process_pdf` loads/chunks text and builds FAISS index.
3. QA chain is initialized with Ollama model.
4. Ask question via `/api/v1/pdf/ask`.

Persistence behavior:
- Runtime uploads are stored under `uploads/`.
- QA state can be persisted in `data/qa_state.pkl.gz` with backup rotation under `data/backups/`.

## Setup Commands

Use the repository virtual environment. System Python 3.13 is not reliable for this repo (import/startup failure observed); Python 3.11 works.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Install developer tools (optional but recommended)

`requirements-dev.txt` includes lint/format/test tooling.

```powershell
python -m pip install -r requirements-dev.txt
```

## Development Workflow

### Start API (simple path)

Verified command:

```powershell
.\.venv\Scripts\python.exe run.py
```

### Start API with hot reload

Verified command:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Access points

- API root: `http://127.0.0.1:8000/`
- Status: `http://127.0.0.1:8000/status`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Web UI: `http://127.0.0.1:8000/static/index.html`

### Docker workflow

Compose services declared and validated from `docker-compose.yml`: `api`, `postgres`, `pgadmin`, `ollama`, `open-webui`.

```powershell
docker compose up -d --build
docker compose ps
docker compose logs -f api
docker compose down
```

Notes:
- Compose warns that the top-level `version` field is obsolete.
- API is exposed on `8000`, Ollama on `11434`, pgAdmin on `5051`, Open WebUI on `3000`, PostgreSQL mapped to host `5433`.

## Testing Instructions

Current repository state:
- `pytest` is available in `.venv`.
- Smoke tests exist under `tests/test_smoke.py`.

Verified command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected current output:
- `2 passed` (count will grow as more tests are added)

Agent expectation when changing code:
- Add or update focused tests where behavior changes.
- Place tests under a `tests/` tree using `test_*.py` naming.
- Re-run `pytest -q` after modifications.

## Code Style and Conventions

Language/tooling:
- Python with FastAPI-style router modules.
- Data models in `app/models.py` (Pydantic).
- Configuration comes from env vars in `app/config.py`.

Formatting/linting tools (from `requirements-dev.txt`):
- `black`
- `isort`
- `pylint`

Run after installing dev dependencies:

```powershell
.\.venv\Scripts\python.exe -m black app
.\.venv\Scripts\python.exe -m isort app
.\.venv\Scripts\python.exe -m pylint app
```

Editing guidance for agents:
- Keep router prefixes and response contracts stable unless explicitly requested.
- Prefer small, scoped edits over broad refactors.
- Preserve env-driven behavior in `app/config.py`.
- If touching persistence, maintain backward compatibility for existing state files when practical.

## Build and Deployment

### Local process deployment

Use Uvicorn directly (example production-like settings):

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Container deployment

```powershell
docker compose up -d --build
```

Container build inputs:
- `Dockerfile.api`
- `requirements.txt`

## Security and Operations Considerations

- Do not commit secrets in `.env`.
- Default Docker Compose credentials in `docker-compose.yml` are development defaults only; replace before real deployments.
- API currently has no authentication/authorization layer; treat as internal/trusted-network by default.
- Uploaded files are user input: validate type/size and keep existing upload guards intact.

## Pull Request Guidelines

Before submitting agent-generated changes:
1. Run app startup verification in `.venv`.
2. Run tests (`pytest -q`) and report status (including no-test state if unchanged).
3. If dev tooling is installed, run format/lint commands and include results.
4. Summarize behavioral changes and any API contract changes.

Suggested PR title format:
- `[backend] short description`
- `[api] short description`
- `[docs] short description`

## Troubleshooting for Agents

### App fails on import/start with FastAPI router error

Symptom seen with system Python 3.13:
- `TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'`

Action:
- Use `.venv` Python 3.11 interpreter for all repo commands.

### Black/isort/pylint command not found

Action:
- Install dev dependencies first:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

### PDF QA state issues

If restored state causes runtime errors:
- Inspect or remove stale persisted files under `data/` and retry.
- Re-upload a PDF to rebuild runtime vector store state.

## Notes on Documentation Drift

Some existing docs reference files/commands not present in this repository (for example `.env.example` and root `app.py`). Prefer the commands in this AGENTS.md and the actual source tree when conflicts appear.
