# DChatty - PDF Question Answering System

DChatty is a robust PDF Question Answering system built with FastAPI, Langchain, and Ollama. It allows users to upload PDF documents and ask questions about their content, receiving accurate answers with source references.

## Features

- **PDF Processing**: Upload and process PDF documents for question answering
- **AI-Powered QA**: Ask natural language questions about document content
- **Source Attribution**: Answers include references to the source text
- **Multiple Model Support**: Switch between different LLM models via Ollama
- **Model Management**: Browse, download and manage Ollama models directly from the UI
- **Optimized Performance**: TF-IDF vectorization and FAISS for fast retrieval
- **Web Interface**: Clean, intuitive UI for easy interaction
- **API Integration**: Comprehensive REST API for integration with other systems

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **AI Components**: 
  - Langchain for document processing workflow
  - FAISS for vector storage and similarity search
  - Ollama for running local LLM models
  - TF-IDF from scikit-learn for efficient document embedding
- **Storage**: File-based state persistence
- **Documentation**: Auto-generated Swagger/OpenAPI docs

## Installation

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) running locally or accessible via network

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dchatty.git
   cd dchatty
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Linux/Mac
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

5. Start the server:
   ```bash
   python run.py
   # Or directly with uvicorn
   uvicorn app.main:app --reload
   ```

### Docker Deployment

For a complete setup with all services, use Docker Compose:

```bash
docker-compose up -d
```

This will start:
- DChatty API server
- Ollama LLM service
- PostgreSQL database
- pgAdmin for database management
- Open WebUI (optional Ollama interface)

## Usage

### Web Interface

Access the web interface at http://localhost:8000/static/index.html

1. Upload a PDF document using the upload button
2. Wait for processing confirmation
3. Select an AI model from the dropdown (if multiple are available)
4. Type your question in the input field
5. View the answer and its source references

### API Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

See `access_instructions.md` for detailed API endpoint information.

## Project Structure

```
.
├── app/                  # Main application code
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration settings
│   ├── file_service.py   # File handling utilities
│   ├── get_answer.py     # Question answering logic
│   ├── main.py           # FastAPI application entry point
│   ├── models.py         # Data models 
│   ├── persistence.py    # State persistence functionality
│   ├── qa_service.py     # QA service with FAISS and embeddings
│   └── routers/          # API route definitions
│       ├── __init__.py   # Routers package initialization
│       ├── files.py      # File management endpoints
│       ├── models.py     # Model management endpoints
│       ├── pdf_qa.py     # PDF QA endpoints
│       ├── status.py     # System status endpoint
│       └── ui.py         # User interface endpoints
├── static/               # Static web files
├── uploads/              # Directory for uploaded files
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile.api        # API Dockerfile
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Configuration

Configuration is handled through environment variables or the `.env` file:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable hot reload for development (default: True)
- `DEBUG`: Enable debug mode (default: True)
- `UPLOAD_DIR`: Directory to store uploaded files (default: uploads)
- `MAX_UPLOAD_SIZE`: Maximum upload file size in bytes (default: 100MB)
- `OLLAMA_MODEL`: Default Ollama model to use (default: phi3)
- `OLLAMA_BASE_URL`: URL for Ollama API (default: http://localhost:11434)

## Ollama Models

The system works with various Ollama models. To add a model:

```bash
ollama pull phi3       # Microsoft's Phi-3 model
ollama pull mistral     # Mistral 7B
ollama pull llama2      # Meta's Llama 2
```

## Troubleshooting

See `access_instructions.md` for detailed troubleshooting information.

## License

MIT
# DChatty - PDF QA System

DChatty is a robust PDF Question Answering system that uses AI to extract information from documents and provide accurate answers to user queries.

## Features

- **PDF Processing**: Upload and process PDF documents
- **AI Question Answering**: Ask questions about document content
- **Multiple Models**: Support for various LLM models via Ollama
- **Vector Database**: Fast document retrieval using FAISS
- **Modern UI**: Clean, responsive interface with drag-and-drop support

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **AI**: Langchain, Ollama, FAISS
- **Containerization**: Docker, Docker Compose
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/dchatty.git
   cd dchatty
   ```

2. Create a .env file from the example
   ```bash
   cp .env.example .env
   ```

3. Start the application using Docker Compose
   ```bash
   docker-compose up -d
   ```

4. Access the application at http://localhost:8000

### Alternative Installation (Local Development)

1. Create a Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

1. Upload a PDF document using the web interface
2. Wait for the document to be processed
3. Select an AI model from the dropdown menu
4. Type your question about the document content
5. View the answer and its source references

## Ollama Models

The application supports various LLM models through Ollama. You can pull and use models like:

- `mistral`: Mistral 7B - A fast and efficient model
- `llama2`: Meta's Llama 2 model
- `phi3`: Microsoft's Phi-3 model

To pull a model using Ollama:
```bash
ollama pull mistral
```

## Configuration

The following environment variables can be configured in the .env file:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable hot reload for development (default: True)
- `DEBUG`: Enable debug mode (default: True)
- `UPLOAD_DIR`: Directory to store uploaded files (default: uploads)
- `MAX_UPLOAD_SIZE`: Maximum upload file size in bytes (default: 100MB)
- `OLLAMA_MODEL`: Default Ollama model to use (default: phi3)
- `EMBEDDING_MODEL`: Model used for text embeddings (default: all-MiniLM-L6-v2)

## Docker Services

- **api**: The main DChatty application
- **ollama**: Ollama LLM service
- **postgres**: PostgreSQL database
- **pgadmin**: PostgreSQL admin interface
- **open-webui**: Alternative Ollama UI (optional)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Langchain](https://www.langchain.com/) for document processing
- [Ollama](https://ollama.ai/) for local LLM support
- [FAISS](https://github.com/facebookresearch/faiss) for vector storage
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
2. **Load the Project**
   - Ensure all project files are in a single directory
   - Make sure you have the following files:
     - `docker-compose.yml`
     - `app.py`
     - `requirements.txt`
     - `Dockerfile.api`

3. **Launch from Docker Desktop**
   - Open Docker Desktop
   - Go to the "Containers" tab
   - Click on "Add project"
   - Browse to your project directory
   - Click "Open"
   - Docker Desktop will detect your docker-compose.yml file
   - Click "Start" to launch all services

   3a. **Running with Uvicorn (without Docker)**
   - Use the run.py script (recommended for all platforms):
     ```bash
     python run.py
     ```
     This script will:
     - Create a virtual environment if needed
     - Install all dependencies
     - Start the application

   - Alternatively, run manually:
     ```bash
     # Install dependencies
     pip install -r requirements.txt

     # Run with Python (recommended for most users)
     python app.py

     # Or use the start scripts
     # Windows: start_server.bat
     # Unix/Linux/Mac: ./start_server.sh (make executable with chmod +x start_server.sh)

     # Or directly with Uvicorn
     uvicorn app:app --host 0.0.0.0 --port 8000 --reload

     # For production environments (multiple workers, no reload)
     uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
     ```

     See `uvicorn_commands.md` for more examples and options.

4. **Alternative: Command Line**
   - Open a terminal/command prompt
   - Navigate to your project directory
   - Run:
   ```bash
   docker-compose up -d
   ```
   - View containers in Docker Desktop UI

5. **Monitor Services**
   - In Docker Desktop, you can:
     - View logs for each service
     - Stop/start individual services
     - Access container shells

### API Documentation

Once running, access the auto-generated API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## File Upload

Files are stored in the `uploads` directory within the container, which is persisted through a Docker volume named `uploads_data`.

Example curl command for file upload:

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.pdf"
```

## Troubleshooting Docker Desktop

### Service Won't Start

1. **Check Port Conflicts**
   - Ensure ports 5432, 5050, 8000, 11434, and 3000 are not already in use
   - In Docker Desktop, go to the failing container and check logs

2. **Resource Issues**
   - Increase resource allocation in Docker Desktop settings
   - Go to Settings → Resources → Advanced

3. **Image Build Failure**
   - Check the build logs in Docker Desktop
   - Ensure all required files exist in your project directory
   - Try building manually: `docker-compose build api`

4. **Volume Permissions**
   - If you encounter permission issues with volumes:
     - Right-click Docker Desktop icon → Settings → Resources → File Sharing
     - Ensure your project directory is in the allowed list

### Accessing Services

- **API Service**: http://localhost:8000
- **pgAdmin**: http://localhost:5050 (login with admin@example.com / admin)
- **Open WebUI**: http://localhost:3000

### Managing Containers
# PDF QA API

A FastAPI backend for PDF processing and question answering using LangChain, FAISS, and Ollama.

## Features

- PDF upload and text extraction using PyPDFLoader
- Text chunking with CharacterTextSplitter
- Embedding generation with SentenceTransformerEmbeddings
- In-memory FAISS vector storage
- Question answering with local Ollama models
- CORS support
- Automatic temporary file cleanup

## Setup

### Prerequisites

- Python 3.8+
- [Ollama](https://github.com/ollama/ollama) installed with the phi3 model (or your model of choice)

### Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file based on `.env.example`

### Running the Server

```bash
python app.py
```

The server will start at http://localhost:8000 by default.

## API Endpoints

### PDF Processing

- `POST /upload/`: Upload a PDF file for processing
- `GET /ask/?query=YOUR_QUESTION`: Ask a question about the uploaded PDF
- `GET /status/`: Get the current status of the QA system

### Legacy File Upload (for backward compatibility)

- `POST /api/upload`: Upload a single file
- `POST /api/upload/multiple`: Upload multiple files

## Docker Support

Build the Docker image:

```bash
docker build -t pdf-qa-api -f Dockerfile.api .
```

Run the container:

```bash
docker run -p 8000:8000 -d pdf-qa-api
```

## Environment Variables

See `.env.example` for available configuration options.

## Project Structure

```
.
├── app/                 # Application package
│   ├── __init__.py      # Package initialization
│   ├── config.py        # Configuration settings
│   ├── file_service.py  # File handling services
│   ├── main.py          # FastAPI application
│   ├── models.py        # Data models
│   ├── qa_service.py    # Question answering services
│   └── routers/         # API routes
│       ├── __init__.py  # Routers package initialization
│       ├── files.py     # File upload routes
│       └── pdf_qa.py    # PDF QA routes
├── app.py              # Application entry point
├── requirements.txt    # Python dependencies
├── Dockerfile.api      # Docker configuration
└── README.md           # Project documentation
```
- Use Docker Desktop's UI to:
  - View container logs (click on a container, then the "Logs" tab)
  - Stop individual services or the entire stack
  - Restart services when needed
  - Delete containers to start fresh
