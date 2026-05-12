# Access Instructions

## Base URLs

When running locally:

- API root: `http://127.0.0.1:8000`
- Status: `http://127.0.0.1:8000/status`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Web UI: `http://127.0.0.1:8000/static/index.html`

## API Endpoints

### PDF QA

- `POST /api/v1/pdf/upload`
  - Multipart form field: `file`
  - Validates extension, size, and PDF signature
- `GET /api/v1/pdf/ask?query=...&model=...`
  - `query` is required
  - `model` is optional

### Files

- `GET /api/v1/files/list`
- `GET /api/v1/files/list?type=pdf`
- `DELETE /api/v1/files/delete/{filename}`

### Models

- `GET /api/v1/models/list`
  - Returns 503 when Ollama is unreachable
- `GET /api/v1/models/info/{model_name}`
- `POST /api/v1/models/change?model_name=...`

## Docker Service Ports

- API: `8000`
- Ollama: `11434`
- PostgreSQL: `5433`
- pgAdmin: `5051`
- Open WebUI: `3000`

## Common Troubleshooting

1. `503 Ollama service is unavailable`
   - Ensure Ollama container/process is running.
   - Verify `OLLAMA_BASE_URL` points to the correct host.

2. `Only PDF files are accepted` or `Uploaded file content is not a valid PDF`
   - Ensure the uploaded file is a real PDF, not a renamed non-PDF file.

3. `No PDF has been uploaded yet`
   - Upload a PDF first through `POST /api/v1/pdf/upload`.

4. Upload rejected with `413`
   - File exceeded `MAX_UPLOAD_SIZE`.
   - Increase the value in `.env` if needed.
