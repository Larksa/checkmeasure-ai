from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import calculations, materials, projects, pdf_processing, debug, agents
from utils.error_logger import log_error, log_info
import traceback
import signal
import sys
import os

app = FastAPI(
    title="Building Measurements API",
    description="Construction material calculation assistant for Australian residential projects",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to prevent server crashes
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions to prevent server crashes"""
    error_id = log_error(exc, "global_exception_handler", additional_info={
        "path": request.url.path,
        "method": request.method,
        "traceback": traceback.format_exc()
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "error_id": error_id,
            "path": request.url.path
        }
    )

# Include routers
app.include_router(calculations.router, prefix="/api/calculations", tags=["calculations"])
app.include_router(materials.router, prefix="/api/materials", tags=["materials"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(pdf_processing.router, prefix="/api/pdf", tags=["pdf"])
app.include_router(debug.router, prefix="/api/debug", tags=["debug"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/")
async def root():
    return {"message": "Building Measurements API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Log when the application starts"""
    log_info(f"Backend starting up - PID: {os.getpid()}", "main.startup")
    log_info(f"Running with timeout_keep_alive=0, no worker recycling", "main.startup")
    
    # Set up signal handlers to understand shutdowns
    def signal_handler(sig, frame):
        sig_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM (Termination)",
            signal.SIGHUP: "SIGHUP (Hangup)",
            signal.SIGUSR1: "SIGUSR1 (User-defined 1)",
            signal.SIGUSR2: "SIGUSR2 (User-defined 2)"
        }
        sig_name = sig_names.get(sig, f"Unknown signal {sig}")
        log_info(f"Received signal: {sig_name} - Backend shutting down", "main.signal_handler")
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    log_info("Signal handlers registered", "main.startup")

@app.on_event("shutdown")
async def shutdown_event():
    """Log when the application shuts down"""
    log_info("Backend shutdown event triggered", "main.shutdown")
    log_info(f"Process {os.getpid()} ending", "main.shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000,
        timeout_keep_alive=0,  # No timeout for keep-alive connections
        ws_ping_interval=None,  # Disable WebSocket ping (we don't use WS)
        ws_ping_timeout=None,   # Disable WebSocket timeout
        limit_max_requests=None # No request limit - don't recycle workers
    )