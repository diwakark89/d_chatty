from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Setup Jinja2 templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir if os.path.exists(templates_dir) else "templates")

# Check if the static/index.html file exists
index_html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "index.html")

@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Serve the main UI page
    """
    # If index.html exists in static folder, serve it directly
    if os.path.exists(index_html_path):
        return FileResponse(index_html_path)

    # Otherwise, use the template if available
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception:
        # Fallback to a simple HTML response
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF QA System</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    color: #333;
                }
                .container {
                    width: 80%;
                    margin: 0 auto;
                    padding: 2rem;
                }
                h1 {
                    color: #2c3e50;
                }
                .card {
                    background: #f9f9f9;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .btn {
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 0.5rem 1rem;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                }
                .btn:hover {
                    background: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>PDF QA System</h1>
                <div class="card">
                    <h2>API is running</h2>
                    <p>The PDF QA API is running successfully. You can:</p>
                    <ul>
                        <li>Upload PDFs for processing</li>
                        <li>Ask questions about uploaded documents</li>
                        <li>Use different AI models for question answering</li>
                    </ul>
                    <p><a href="/docs" class="btn">View API Documentation</a></p>
                </div>
            </div>
        </body>
        </html>
        """)

@router.get("/app", response_class=HTMLResponse)
async def get_app_ui(request: Request):
    """
    Serve the application UI page
    """
    # Redirect to index.html in static folder if it exists
    if os.path.exists(index_html_path):
        return FileResponse(index_html_path)

    # Otherwise try the template
    try:
        return templates.TemplateResponse("app.html", {"request": request})
    except Exception:
        # Redirect to main index page
        return get_index(request)
