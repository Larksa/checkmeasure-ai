# Vercel serverless function handler
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the FastAPI app
from backend.main import app

# Export handler for Vercel
handler = app