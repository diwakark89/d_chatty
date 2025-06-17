# Simple HTTP server to serve the static HTML interface
import http.server
import socketserver
import os
import webbrowser
import threading
import time

# Create static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Configuration
PORT = 8080
HANDLER = http.server.SimpleHTTPRequestHandler

print(f"Starting simple HTTP server on port {PORT}...")
print(f"Serving files from: {os.getcwd()}")

# Create the server
with socketserver.TCPServer(("", PORT), HANDLER) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print(f"Open your browser to: http://localhost:{PORT}/static/index.html")

    # Open browser after a short delay
    def open_browser():
        time.sleep(1)
        webbrowser.open(f'http://localhost:{PORT}/static/index.html')

    threading.Thread(target=open_browser).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
