#!/usr/bin/env python
"""
Run the FastAPI server.

Usage:
    # Activate venv first:
    # Windows: venv\\Scripts\\activate
    # Linux/Mac: source venv/bin/activate

    # Then run:
    python run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8802,
        reload=True
    )
