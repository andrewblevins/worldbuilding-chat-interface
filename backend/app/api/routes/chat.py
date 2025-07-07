"""
Chat API routes for the Worldbuilding Chat Interface.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

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
    """Send a message to the chat interface."""
    # TODO: Implement message processing and MCP tool integration
    return ChatResponse(
        content=f"Echo: {message.content}",
        role="assistant"
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