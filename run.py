# run.py - Entry point for the application
import uvicorn
import os

# Detect the proper application module path
def find_app_module():
    if os.path.exists("app/main.py"):
        return "app.main:app"  # Standard FastAPI structure with app/main.py
    elif os.path.exists("main.py"):
        return "main:app"      # FastAPI app in main.py
    elif os.path.exists("app.py"):
        return "app:app"       # FastAPI app in app.py
    else:
        raise FileNotFoundError("Could not find FastAPI application file (main.py, app.py, or app/main.py)")

if __name__ == "__main__":
    try:
        app_module = find_app_module()
        print(f"Starting FastAPI application from {app_module}")

        # Check if required packages are installed
        try:
            # Try importing key dependencies before starting the server
            import fastapi
            import langchain
            # If we get here, the imports succeeded
            print("✓ Core dependencies verified")
        except ImportError as e:
            print(f"WARNING: Missing dependency: {e}")
            print("Run 'pip install -r requirements.txt' to install required packages")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                import sys
                sys.exit(1)

        # Start the server with reload enabled
        uvicorn.run(app_module, host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"ERROR: Failed to start server: {e}")
        print("Try running 'fix_dependencies.bat' to resolve dependency issues")
        import sys
        sys.exit(1)