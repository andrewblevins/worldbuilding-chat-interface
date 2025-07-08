"""
Chat API routes for the Worldbuilding Chat Interface.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, AsyncGenerator
from loguru import logger
import json
import asyncio

from ...services.claude_service import claude_service

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    content: str
    role: str = "user"
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response model."""
    content: str
    role: str = "assistant"
    tool_calls: List[Dict[str, Any]] = []
    files_created: List[str] = []


async def stream_response(message_content: str) -> AsyncGenerator[str, None]:
    """Stream the response from Claude with tool execution."""
    try:
        # Process the message and get the response
        response = await claude_service.process_with_tools(message_content)
        
        # Simulate streaming by chunking the response
        content = response["content"]
        tool_calls = response.get("tool_calls", [])
        files_created = response.get("files_created", [])
        
        # Send the content in chunks
        words = content.split(' ')
        current_chunk = ""
        
        for i, word in enumerate(words):
            current_chunk += word + " "
            
            # Send chunks of 3-5 words
            if len(current_chunk.split()) >= 4 or i == len(words) - 1:
                chunk_data = {
                    "type": "content",
                    "content": current_chunk.strip(),
                    "is_final": i == len(words) - 1
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                current_chunk = ""
                await asyncio.sleep(0.05)  # Small delay for streaming effect
        
        # Send tool calls if any
        if tool_calls:
            tool_data = {
                "type": "tools",
                "tool_calls": tool_calls,
                "files_created": files_created
            }
            yield f"data: {json.dumps(tool_data)}\n\n"
        
        # Send end signal
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
        
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e)
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/send")
async def send_message(message: ChatMessage):
    """Send a message to the chat interface and get Claude's response."""
    try:
        logger.info(f"Processing chat message: {message.content[:100]}... (stream: {message.stream})")
        
        if message.stream:
            # Return streaming response
            return StreamingResponse(
                stream_response(message.content),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        else:
            # Return regular response
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