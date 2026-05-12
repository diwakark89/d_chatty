# Troubleshooting Guide

## PDF Upload Issues

### Error: "index out of range"

This error occurs when the system cannot properly process the PDF document. This may happen due to:

1. **Empty or corrupted PDF files**
2. **Scanned documents without OCR**
3. **Highly complex document structures**
4. **Password-protected PDFs**

**Solution:**

- Try a different PDF document
- Ensure the PDF has extractable text content
- For scanned documents, run them through an OCR tool first
- Remove password protection from the document

### Error: "sparse array length is ambiguous"

This is related to the vector embedding process:

1. **FAISS compatibility issues with sparse matrices**
2. **Embedding model configuration**

**Solution:**

- Update to the latest version of the application
- Try using a different embedding model by updating the `.env` file
- Restart the application after changing configuration

## System Status Always Shows "Not Ready"

1. **Check if the backend service is running**
2. **Verify network connectivity between frontend and API**
3. **Check for error messages in browser console**

**Solution:**

- Click the refresh button in the System Info panel
- Try uploading a simple PDF document
- Check that the OLLAMA service is running

## Docker Deployment Issues

### FAISS Library Errors

FAISS may have compatibility issues with certain hardware or Docker setups:

1. **Missing AVX2 support**: This is expected and the system should fall back to standard mode
2. **Version conflicts**: Make sure all Python packages are compatible

**Solution:**

- Rebuild the Docker image with `docker-compose build --no-cache api`
- Update your Docker image to the latest version
- Ensure your system meets the minimum requirements

## For Developers

If you're developing or extending this application:

1. Use the `requirements-dev.txt` file for development dependencies
2. Check logs for detailed error information
3. The FAISS vector store requires dense arrays, so sparse matrices need conversion
4. For embedding issues, consider using a different embedding model
