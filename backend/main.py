from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import calculations, materials, projects, pdf_processing, debug, agents
from utils.error_logger import log_error
import traceback

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
    from utils.error_logger import log_info
    import os
    log_info(f"Backend starting up - PID: {os.getpid()}", "main.startup")

@app.on_event("shutdown")
async def shutdown_event():
    """Log when the application shuts down"""
    from utils.error_logger import log_info
    log_info("Backend shutting down", "main.shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)