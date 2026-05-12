import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.routers import files, models, pdf_qa, status, ui

logging.basicConfig(level=logging.INFO if config.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF QA API",
    description="API for querying PDF documents using local LLM models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=config.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(status.router)
app.include_router(pdf_qa.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(ui.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "PDF QA API is running"}


@app.get("/api", tags=["API"])
async def api_root():
    return {"status": "ok", "message": "PDF QA API is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=config.HOST, port=config.PORT, reload=config.RELOAD)
