#!/usr/bin/env python3
"""
FastAPI Server Startup Script
Run this script from the web-app directory to start the backend server.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory for relative imports
os.chdir(str(backend_dir))

# Now import and run
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting Watermark Removal Backend Server...")
    print(f"Host: {settings.HOST}:{settings.PORT}")
    print(f"Device: {settings.DEVICE}")
    print(f"Debug: {settings.DEBUG}")
    print(f"\nAPI Documentation: http://localhost:{settings.PORT}/docs")
    print(f"ReDoc: http://localhost:{settings.PORT}/redoc")
    print(f"\nPress CTRL+C to stop the server.\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
