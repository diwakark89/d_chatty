# Accessing Your DChatty FastAPI Application

## Basic Access

Your FastAPI application is running on `http://0.0.0.0:8000`, which means it's accessible through:

- `http://localhost:8000` (from the same machine)
- `http://your-ip-address:8000` (from other devices on the same network)

## Available Endpoints

### API Endpoints

- PDF Processing:
  - `POST /api/v1/pdf/upload`: Upload a PDF file for processing
  - `GET /api/v1/pdf/ask?query=YOUR_QUESTION`: Ask a question about the uploaded PDF

- File Management:
  - `GET /api/v1/files/list`: List all uploaded files
  - `DELETE /api/v1/files/delete?filename=YOUR_FILE.pdf`: Delete an uploaded file

- Model Management:
  - `GET /api/v1/models/list`: List locally available Ollama models
  - `GET /api/v1/models/info?model=MODEL_NAME`: Get info about a specific model
  - `GET /api/v1/models/available`: Get list of models available from Ollama website
  - `POST /api/v1/models/download`: Download a model from Ollama (requires model_name in body)
  - `GET /api/v1/models/download-status/{model_name}`: Check download status of a model
  - `POST /api/v1/models/delete`: Delete a model from local storage

- System Status:
  - `GET /status`: Get the current system status

### Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Web Interface

The web interface is available at:
- `http://localhost:8000/static/index.html`

## Using Docker

If you're using Docker, the application is accessible at the same URLs, but you can also access related services:

- **Ollama API**: `http://localhost:11434`
- **Open WebUI** (Ollama interface): `http://localhost:3000`
- **pgAdmin** (Database management): `http://localhost:5051` (login with admin@example.com / admin)

## API Authentication

Currently, the API does not require authentication. In production environments, you should enable authentication by:

1. Configuring API keys or OAuth in the `.env` file
2. Setting up proper CORS restrictions

## Troubleshooting

### Common Issues

1. **Cannot connect to the application**
   - Ensure the server is running
   - Check that the port 8000 is not blocked by a firewall
   - Verify that your Docker containers are running if using Docker

2. **PDF processing fails**
   - Ensure the PDF is not password-protected
   - Check that the PDF file is not corrupted
   - Make sure Ollama service is running and accessible

3. **Slow response times**
   - Large PDFs may take longer to process
   - First-time model loading in Ollama can be slow
   - Check system resources (CPU, RAM) if performance is consistently poor

### Logs

Access logs by:

- Viewing terminal output when running locally
- Using Docker logs: `docker logs chatty_api`
- Checking pgAdmin for database logs

## Development Setup

For development, enable hot reload:

1. Set `RELOAD=True` in your `.env` file
2. Run with uvicorn directly: `uvicorn app.main:app --reload`

This allows changes to be immediately reflected without restarting the server.
