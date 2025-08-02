# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CheckMeasureAI is an AI-powered construction material calculation assistant designed for Australian structural engineers and builders. It automates material takeoffs from architectural drawings and generates professional cutting lists compliant with Australian standards.

## Development Commands

### Docker Development (Recommended - Solves macOS Issues)

```bash
# First time setup
./setup-docker.sh

# Start all services with Docker
make up

# View logs
make logs

# Stop services
make down

# Clean everything
make clean

# Access backend shell
make shell

# This Docker setup:
# - Eliminates macOS process management issues
# - Provides consistent environment
# - Auto-restarts on failure
# - Includes health checks
# - Persists uploaded PDFs
```

### Traditional Development (Alternative)

```bash
# Start both backend and frontend servers with one command
./scripts/dev.sh

# This will:
# - Check if ports are already in use
# - Start backend on http://localhost:8000
# - Start frontend on http://localhost:3000
# - Handle cleanup on Ctrl+C
# - Show clear status messages

# Stop all servers cleanly
./scripts/stop.sh
```

### Manual Server Start (Alternative)

```bash
cd backend

# Install dependencies (first time setup)
pip install -r requirements.txt

# Run development server
python3 main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run basic tests
python3 test_basic.py

# Run specific tests with pytest
python3 -m pytest tests/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Full System Development

```bash
# Terminal 1: Backend
cd backend && python3 main.py

# Terminal 2: Frontend  
cd frontend && npm start

# Access at http://localhost:3000
```

## Architecture & Key Components

### Backend Structure

The backend uses FastAPI with a modular architecture:

- **API Routers** (`api/routers/`): REST endpoints for calculations, materials, PDF processing, and multi-agent operations
- **Core Business Logic** (`core/`):
  - `calculators/joist_calculator.py`: Implements AS1684-compliant joist calculations
  - `materials/material_system.py`: Material specifications and selection logic
  - `agents/`: Multi-agent system for advanced calculations and optimization
- **PDF Processing** (`pdf_processing/`): PyMuPDF-based drawing analysis with Claude Vision integration
- **Output Generation** (`output_formats/`): Professional cutting list formatting

### Frontend Structure  

React/TypeScript application with:

- **PDF Viewer** (`components/pdf-viewer/`): Interactive PDF display with area selection
- **Selection Tools** (`components/selection-tools/`): Drawing measurement extraction
- **Calculation Interface** (`components/calculation-review/`): Material specifications and results
- **State Management** (`stores/appStore.ts`): Zustand-based state management
- **API Client** (`utils/api.ts`): Axios-based backend communication

### Multi-Agent System

The project includes an advanced multi-agent architecture:

- **Agent Manager** (`core/agents/agent_manager.py`): Orchestrates specialized agents
- **Project Orchestrator** (`core/agents/project_orchestrator.py`): Coordinates complex workflows
- **Specialized Agents** (`core/agents/specialized/`): Task-specific calculation agents
- **Event Bus** (`core/agents/event_bus.py`): Inter-agent communication

## Australian Standards Compliance

### Materials (AS1684)

- **LVL Sizes**: 150x45, 200x45, 240x45, 200x63 E13 LVL
- **Treated Pine**: 90x45 H2 MGP10, 70x35 E10 H2  
- **Standard Lengths**: 3.0m to 7.8m in 0.6m increments
- **Standard Spacings**: 300mm, 450mm, 600mm centers

### Reference Coding System

- **Levels**: GF (Ground Floor), L1 (Level 1), RF (Roof)
- **Components**: J (Joists), B (Blocking), ST (Studs), RX (Rafters)
- **Format**: `{Level}-{Component}{Sequence}` (e.g., L1-J1)

## Development Workflow

### Adding New Features

1. **New Calculators**: Create in `core/calculators/`, follow `joist_calculator.py` pattern
2. **API Endpoints**: Add to appropriate router in `api/routers/`
3. **Frontend Components**: Add to `components/`, update `App.tsx`
4. **State Management**: Update `stores/appStore.ts` as needed

### Testing Requirements

- Always run `python3 test_basic.py` after backend changes
- Test API endpoints: `curl http://localhost:8000/api/[endpoint]`
- Verify cutting list format matches client specifications
- Check calculations against manual verification

### Code Standards

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode enabled, proper interface definitions
- **API**: RESTful conventions, comprehensive error handling
- **Logging**: Use `enhanced_logger.py` for all backend logging

## Critical Implementation Notes

1. **Material Selection**: All assumptions must be logged for engineer review
2. **Calculation Transparency**: Show step-by-step formula application
3. **PDF Processing**: Handle scale detection and unit conversion
4. **Error Handling**: Graceful degradation with informative messages
5. **Performance**: Async operations for PDF processing and calculations

## Current Development Status

- ✅ Core joist calculations with AS1684 compliance
- ✅ Material system with comprehensive specifications
- ✅ PDF viewer with interactive selection tools
- ✅ Multi-agent system architecture
- ✅ Professional cutting list generation
- 🔄 Advanced PDF dimension extraction (in progress)
- 📋 Wall framing and rafter calculators (planned)

## Environment Requirements

### Docker (Recommended)
- Docker Desktop installed and running
- 4GB+ RAM allocated to Docker
- 10GB+ free disk space

### Traditional Setup
- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- PyMuPDF for PDF processing
- Claude API access for vision analysis (optional)

## Docker Troubleshooting

### Common Issues

1. **Build takes forever**: First build downloads all dependencies (normal - can take 5-10 minutes)
2. **Port already in use**: Run `./scripts/stop.sh` first or `docker-compose down`
3. **Permission denied**: Make sure scripts are executable: `chmod +x *.sh`
4. **M1 Mac issues**: The `docker-compose.override.yml` forces x86 platform if needed
5. **Backend dies after idle**: This is exactly what Docker solves! Use Docker instead of traditional setup

### Quick Fixes

```bash
# Reset everything
make clean
docker system prune -f

# Rebuild from scratch
make build

# Check what's running
docker-compose ps
docker logs checkmeasure-backend
docker logs checkmeasure-frontend
```