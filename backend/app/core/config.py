"""
Configuration settings for the Worldbuilding Chat Interface backend.
"""

import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="../.env")


class Settings(BaseModel):
    """Application settings."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Worldbuilding Chat Interface"
    VERSION: str = "0.1.0"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://worldbuilding-chat.vercel.app",
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # MCP Settings
    MCP_SERVER_PATH: str = os.getenv("MCP_SERVER_PATH", "../../vibe-worldbuilding-mcp")
    
    # FAL API (for image generation)
    FAL_KEY: str = os.getenv("FAL_KEY", "")
    
    # File Storage
    WORLDS_DIR: str = os.getenv("WORLDS_DIR", "worlds")
    MAX_WORLD_SIZE_MB: int = int(os.getenv("MAX_WORLD_SIZE_MB", "100"))
    
    # WebSocket Settings
    WS_MAX_CONNECTIONS: int = int(os.getenv("WS_MAX_CONNECTIONS", "100"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Frontend serving (for production)
    SERVE_FRONTEND: bool = os.getenv("SERVE_FRONTEND", "false").lower() == "true"
    
    # Anthropic Claude API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")


# Create settings instance
settings = Settings()

# Export commonly used values
__all__ = ["settings"] 