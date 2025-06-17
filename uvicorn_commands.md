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
