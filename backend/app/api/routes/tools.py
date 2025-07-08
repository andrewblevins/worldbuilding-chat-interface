"""
Tools API routes for the Worldbuilding Chat Interface.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from loguru import logger

from ...core.mcp_client import mcp_client

router = APIRouter()


class ToolRequest(BaseModel):
    """Tool execution request model."""
    tool_name: str
    parameters: Dict[str, Any]


class ToolResponse(BaseModel):
    """Tool execution response model."""
    success: bool
    result: str
    files_created: List[str] = []
    error: str = None


class ToolInfo(BaseModel):
    """Tool information model."""
    name: str
    category: str
    description: str


@router.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a specific MCP tool."""
    try:
        logger.info(f"Executing tool: {request.tool_name} with parameters: {request.parameters}")
        
        # Execute the tool through the MCP client
        result = await mcp_client.execute_tool(request.tool_name, request.parameters)
        
        return ToolResponse(
            success=result["success"],
            result=result["result"],
            files_created=result.get("files_created", []),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing tool: {str(e)}"
        )


@router.get("/list", response_model=List[ToolInfo])
async def list_tools():
    """List all available MCP tools."""
    try:
        available_tools = mcp_client.get_available_tools()
        
        return [
            ToolInfo(
                name=tool["name"],
                category=tool["category"],
                description=tool["description"]
            )
            for tool in available_tools
        ]
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing tools: {str(e)}"
        )


@router.get("/status")
async def get_tools_status():
    """Get the status of the MCP tools system."""
    available_tools = mcp_client.get_available_tools()
    
    return {
        "mcp_available": mcp_client.available,
        "tools_count": len(available_tools),
        "tools": [tool["name"] for tool in available_tools]
    }


@router.get("/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get detailed information about a specific tool."""
    tool_info = mcp_client.get_tool_by_name(tool_name)
    
    if not tool_info:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found"
        )
        
    return tool_info 