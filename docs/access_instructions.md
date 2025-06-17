# Accessing Your DChatty FastAPI Application

## Basic Access

Your FastAPI application is running on `http://0.0.0.0:8000`, which means it's accessible through:

- `http://localhost:8000` (from the same machine)
- `http://your-ip-address:8000` (from other devices on the same network)

## Available Endpoints

### Documentation

The built-in FastAPI documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

- Root endpoint: `http://localhost:8000/`
- Upload a file: `http://localhost:8000/api/upload` (POST request)

## Using the API

### From a Web Browser

1. Open your web browser and navigate to `http://localhost:8000/docs`
2. This will open the Swagger UI where you can test all available endpoints
3. Click on any endpoint to expand it
4. Click the "Try it out" button
5. Fill in any required parameters
6. Click "Execute" to send the request

### Using Postman

1. Open Postman and create a new request
2. Set the request method (GET, POST, etc.) and URL (e.g., `http://localhost:8000/api/upload`)
3. For file uploads:
   - Go to the "Body" tab
   - Select "form-data"
   - Add a key named "file" and set its type to "File"
   - Select the file you want to upload
4. Click "Send" to execute the request

### Using curl

```bash
# Test the root endpoint
curl http://localhost:8000/

# Upload a file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/your/file.pdf"
```

## Troubleshooting

- If you can't access the API from another device, ensure your firewall allows connections to port 8000
- If you see CORS errors in your browser console, check that your frontend application's origin is included in the allowed origins list
- For connection refused errors, verify that the server is running and listening on the correct port
