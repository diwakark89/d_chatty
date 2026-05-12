# Access Instructions

## Local URLs

- API root: `http://127.0.0.1:8000/`
- Status: `http://127.0.0.1:8000/status`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Web UI: `http://127.0.0.1:8000/static/index.html`

## Core API Routes

- `POST /api/v1/pdf/upload`
- `GET /api/v1/pdf/ask?query=...&model=...`
- `GET /api/v1/files/list`
- `DELETE /api/v1/files/delete/{filename}`
- `GET /api/v1/models/list`
- `GET /api/v1/models/info/{model_name}`
- `POST /api/v1/models/change?model_name=...`

## Notes

- Model listing now returns HTTP 503 if Ollama is unavailable.
- PDF uploads enforce file size and content-signature checks.
- File deletion validates filenames to block traversal attempts.
