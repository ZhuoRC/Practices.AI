"""
AI Video Splitter - Backend Entry Point

Run this script to start the backend server.
"""

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
