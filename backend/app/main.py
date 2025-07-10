"""
Main FastAPI application for the Worldbuilding Chat Interface.

This serves as the backend API that integrates with the Vibe Worldbuilding MCP
to provide a chat interface for world creation.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from .core.config import settings
from .api.routes import chat, tools, worlds, files
from .api.websocket import websocket_endpoint
from .services.file_watcher import file_watcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Worldbuilding Chat Interface backend...")
    
    # Ensure worlds directory exists
    worlds_dir = Path("worlds")
    worlds_dir.mkdir(exist_ok=True)
    
    # Log MCP availability
    from .core.mcp_client import mcp_client
    logger.info(f"MCP tools available: {mcp_client.available}")
    if mcp_client.available:
        tools_count = len(mcp_client.get_available_tools())
        logger.info(f"Loaded {tools_count} MCP tools")
    else:
        logger.warning("MCP tools not available - running in demo mode")
    
    # Start file watcher for real-time updates
    try:
        file_watcher.start()
        logger.info("File watcher started for real-time world updates")
    except Exception as e:
        logger.warning(f"Could not start file watcher: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Worldbuilding Chat Interface backend...")
    
    # Stop file watcher
    try:
        file_watcher.stop()
        logger.info("File watcher stopped")
    except Exception as e:
        logger.error(f"Error stopping file watcher: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(tools.router, prefix=f"{settings.API_V1_STR}/tools", tags=["tools"])
app.include_router(worlds.router, prefix=f"{settings.API_V1_STR}/worlds", tags=["worlds"])
app.include_router(files.router, prefix=f"{settings.API_V1_STR}/files", tags=["files"])

# WebSocket endpoint
app.add_websocket_route("/ws", websocket_endpoint)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from .core.mcp_client import mcp_client
    
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mcp_available": mcp_client.available,
        "file_watcher_running": file_watcher.running,
        "environment": settings.ENVIRONMENT
    }

@app.get("/version")
async def version_check():
    """Version check endpoint to test auto-reload."""
    import time
    return {
        "version": "dev-auto-reload", 
        "reload_test": int(time.time()),
        "debug_logs_enabled": True
    }

# Serve static files in production
if settings.SERVE_FRONTEND:
    frontend_dist = Path("frontend/dist")
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
        logger.info("Serving frontend from /frontend/dist")
    else:
        logger.warning("Frontend dist directory not found - frontend will not be served")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    ) 