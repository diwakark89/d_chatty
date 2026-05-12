# Uvicorn Commands for Running FastAPI

## Basic Commands

### Standard Development Server (with hot reload)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Production Server (no hot reload)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Notes on Persistence

The application now supports persistence of uploaded PDFs across server restarts. However, there are some important considerations:

- In development mode with `--reload`, when code changes are detected, the application will restart and the saved state will be reloaded
- In production mode with multiple workers (`--workers`), each worker process must load the same saved state
- For more details on persistence, see the `docs/persistence.md` file

### Custom Log Level
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## Environment Variables

To use environment variables from your .env file:

```bash
# Load from config.py which uses dotenv
uvicorn app:app --host $(python -c "import app.config; print(app.config.HOST)") --port $(python -c "import app.config; print(app.config.PORT)") --reload $(python -c "import app.config; print('--reload' if app.config.RELOAD else '')")
```

## SSL/HTTPS Configuration

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem
```

## Performance Tuning

### Multi-worker Setup (Gunicorn + Uvicorn)

For production environments, Gunicorn with Uvicorn workers is recommended:

```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Uvicorn with Multiple Workers

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Memory Optimization

The application has been optimized for better memory usage. To monitor memory consumption:

```bash
# Install psutil if not already installed
pip install psutil

# Run with memory monitoring enabled
MEMORY_MONITORING=true uvicorn app:app --host 0.0.0.0 --port 8000
```

### Vector Store Performance

The FAISS vector store has been optimized with these considerations:

1. **Sparse vs. Dense Embeddings**: Using TF-IDF with sparse matrices for efficiency
2. **Limiting Vocabulary Size**: Using `max_features` parameter to control memory usage
3. **Caching**: Query responses are cached to improve repeated question performance

### Ollama LLM Optimization

To optimize Ollama performance:

```bash
# Set Ollama to use smaller, faster models for development
export OLLAMA_MODEL=phi3:mini  # Smaller, faster model

# Or set in .env file
OLLAMA_MODEL=phi3:mini
```

## App-specific Commands

### Start with Environment-specific Settings

```bash
# Development
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Testing
uvicorn app:app --host 127.0.0.1 --port 8000

# Production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log
```
# Uvicorn Commands for Running FastAPI

## Project Structure Options

Before running Uvicorn, make sure you know where your FastAPI app is defined. Common structures include:

1. **Standard Package Structure** - app/main.py contains a FastAPI instance named `app`
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Simple Structure** - app.py in the root directory with a FastAPI instance named `app`
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Alternative Simple Structure** - main.py in the root directory with a FastAPI instance named `app`
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Basic Commands

### Standard Development Server (with hot reload)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Server (no hot reload)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Custom Log Level
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## Environment Variables

To use environment variables from your .env file:

```bash
# Load from config.py which uses dotenv
uvicorn app.main:app --host $(python -c "import app.config; print(app.config.HOST)") --port $(python -c "import app.config; print(app.config.PORT)") --reload $(python -c "import app.config; print('--reload' if app.config.RELOAD else '')")
```

## SSL/HTTPS Configuration

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem
```

## Performance Tuning

### Multi-worker Setup (Gunicorn + Uvicorn)

For production environments, Gunicorn with Uvicorn workers is recommended:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Uvicorn with Multiple Workers

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## App-specific Commands

### Start with Environment-specific Settings

```bash
# Development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Testing
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log
```

### Accessing Logs

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug > app.log 2>&1
```
### Accessing Logs

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --log-level debug > app.log 2>&1
```
