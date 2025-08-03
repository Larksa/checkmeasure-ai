from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route handling
        if self.path == '/health':
            response = {"status": "healthy", "version": "demo"}
        elif self.path == '/':
            response = {"message": "CheckMeasureAI Backend API", "endpoints": ["/health", "/api/test"]}
        elif self.path == '/api/test':
            response = {"message": "API is working!", "data": "This is a demo backend"}
        else:
            response = {"error": "Not found", "path": self.path}
            
        self.wfile.write(json.dumps(response).encode())
        
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_POST(self):
        # Basic POST handler
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"message": "POST received", "demo": True}
        self.wfile.write(json.dumps(response).encode())