import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import our custom modules
from app import config
from app.routers import status

# Configure logging
logging.basicConfig(level=logging.INFO if config.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF QA API",
    description="API for PDF processing and question answering",
    version="1.0.0",
    debug=config.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

# Mount static files directory if it exists
if os.path.exists('static'):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Add the non-prefixed status endpoint
app.include_router(status.router)

# Status endpoint for root level access
@app.get("/status")
async def get_root_status():
    return status.get_status()

# Root endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "PDF QA API is running"}

# Only import and include the other routers after status is set up
from app.routers import pdf_qa, files, models, ui

# Set up versioned API routers
app.include_router(pdf_qa.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")

# Include the UI router
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app import config
from app.routers import pdf_qa, files, models, ui, status

# Configure logging
logging.basicConfig(level=logging.INFO if config.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF QA API",
    description="API for querying PDF documents using LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=config.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(status.router)
app.include_router(pdf_qa.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(ui.router)

# Root endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "PDF QA API is running"}

# Make status endpoint available at root level too
@app.get("/status")
async def get_root_status():
    return status.get_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )
# API root endpoint - redirect to docs
@app.get("/api", tags=["API"])
async def api_root():
    return {"status": "ok", "message": "PDF QA API is running", "docs": "/docs"}
