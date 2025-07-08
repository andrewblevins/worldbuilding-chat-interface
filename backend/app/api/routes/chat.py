"""
Chat API routes for the Worldbuilding Chat Interface.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from loguru import logger

from ...services.claude_service import claude_service

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    content: str
    role: str = "user"


class ChatResponse(BaseModel):
    """Chat response model."""
    content: str
    role: str = "assistant"
    tool_calls: List[Dict[str, Any]] = []
    files_created: List[str] = []


@router.post("/send", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """Send a message to the chat interface and get Claude's response."""
    try:
        logger.info(f"Processing chat message: {message.content[:100]}...")
        
        # Use Claude service to generate response and potentially execute tools
        response = await claude_service.process_with_tools(message.content)
        
        return ChatResponse(
            content=response["content"],
            role=response["role"],
            tool_calls=response.get("tool_calls", []),
            files_created=response.get("files_created", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/tools")
async def get_available_tools():
    """Get list of available MCP tools."""
    # TODO: Implement tool discovery from MCP server
    return {
        "tools": [
            {
                "name": "instantiate_world",
                "description": "Create a new world project",
                "category": "world"
            },
            {
                "name": "create_taxonomy_folders",
                "description": "Create organized categories for your world",
                "category": "taxonomy"
            },
            {
                "name": "create_world_entry",
                "description": "Add detailed entries to your world",
                "category": "entry"
            },
            {
                "name": "generate_image_from_markdown_file",
                "description": "Create visuals for your content",
                "category": "image"
            },
            {
                "name": "build_static_site",
                "description": "Generate a navigable website from your world",
                "category": "site"
            }
        ]
    } 