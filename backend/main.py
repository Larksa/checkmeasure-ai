from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import calculations, materials, projects, pdf_processing, debug, agents

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)