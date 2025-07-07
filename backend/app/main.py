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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Worldbuilding Chat Interface backend...")
    
    # Ensure worlds directory exists
    worlds_dir = Path("worlds")
    worlds_dir.mkdir(exist_ok=True)
    
    # Initialize MCP client connection
    # TODO: Initialize MCP client here
    
    yield
    
    logger.info("Shutting down Worldbuilding Chat Interface backend...")


# Create FastAPI app
app = FastAPI(
    title="Worldbuilding Chat Interface API",
    description="Backend API for the Vibe Worldbuilding MCP chat interface",
    version="0.1.0",
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
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(worlds.router, prefix="/api/worlds", tags=["worlds"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

# WebSocket endpoint
app.add_websocket_route("/ws", websocket_endpoint)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "worldbuilding-chat-interface"}

# Serve static files in production
if os.getenv("ENVIRONMENT") == "production":
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 