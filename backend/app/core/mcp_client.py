"""
MCP Client for integrating with the Vibe Worldbuilding MCP server.

This module handles communication with the vibe-worldbuilding MCP tools
and provides a clean interface for the FastAPI backend.
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger

# Add the vibe-worldbuilding MCP to the Python path
MCP_PATH = Path(__file__).parent.parent.parent.parent / "vibe-worldbuilding-mcp"
if MCP_PATH.exists():
    sys.path.insert(0, str(MCP_PATH))

try:
    # Import MCP tool handlers
    from vibe_worldbuilding.tools.world import handle_world_tool, WORLD_HANDLERS
    from vibe_worldbuilding.tools.taxonomy import handle_taxonomy_tool, TAXONOMY_HANDLERS  
    from vibe_worldbuilding.tools.entries import handle_entry_tool, ENTRY_HANDLERS
    from vibe_worldbuilding.tools.images import handle_image_tool, IMAGE_HANDLERS
    from vibe_worldbuilding.tools.site import handle_site_tool, SITE_HANDLERS
    MCP_AVAILABLE = True
    logger.info("Successfully imported vibe-worldbuilding MCP tools")
except ImportError as e:
    logger.warning(f"Could not import MCP tools: {e}")
    MCP_AVAILABLE = False


class MCPClient:
    """Client for communicating with the Vibe Worldbuilding MCP server."""
    
    def __init__(self):
        self.available = MCP_AVAILABLE
        self.tool_handlers = {}
        
        if self.available:
            self.tool_handlers.update({
                **WORLD_HANDLERS,
                **TAXONOMY_HANDLERS,
                **ENTRY_HANDLERS,
                **IMAGE_HANDLERS,
                **SITE_HANDLERS,
            })
            
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific MCP tool with the given parameters."""
        if not self.available:
            raise RuntimeError("MCP tools are not available")
            
        if tool_name not in self.tool_handlers:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        try:
            # Route to appropriate handler based on tool name
            if tool_name in WORLD_HANDLERS:
                result = await handle_world_tool(tool_name, parameters)
            elif tool_name in TAXONOMY_HANDLERS:
                result = await handle_taxonomy_tool(tool_name, parameters)
            elif tool_name in ENTRY_HANDLERS:
                result = await handle_entry_tool(tool_name, parameters)
            elif tool_name in IMAGE_HANDLERS:
                result = await handle_image_tool(tool_name, parameters)
            elif tool_name in SITE_HANDLERS:
                result = await handle_site_tool(tool_name, parameters)
            else:
                raise ValueError(f"No handler found for tool: {tool_name}")
                
            # Convert MCP result to our format
            if isinstance(result, list) and len(result) > 0:
                # MCP returns a list of TextContent objects
                text_result = result[0].text if hasattr(result[0], 'text') else str(result[0])
                
                return {
                    "success": True,
                    "result": text_result,
                    "files_created": self._extract_files_from_result(text_result),
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            else:
                return {
                    "success": False,
                    "result": "Tool execution failed - no result returned",
                    "error": "Empty result from MCP tool",
                    "tool_name": tool_name,
                    "parameters": parameters
                }
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "result": f"Tool execution failed: {str(e)}",
                "error": str(e),
                "tool_name": tool_name,
                "parameters": parameters
            }
    
    def _extract_files_from_result(self, result_text: str) -> List[str]:
        """Extract file paths from the tool result text."""
        files = []
        
        # Look for common file creation patterns
        import re
        
        # Pattern for "Created file: path/to/file"
        created_pattern = r"[Cc]reated (?:file|entry|taxonomy|world)[:\s]+([^\s\n]+)"
        files.extend(re.findall(created_pattern, result_text))
        
        # Pattern for "Saved to: path/to/file" 
        saved_pattern = r"[Ss]aved to[:\s]+([^\s\n]+)"
        files.extend(re.findall(saved_pattern, result_text))
        
        # Pattern for file paths in general (*.md, *.png, etc.)
        file_pattern = r"([^\s]+\.[a-zA-Z]{2,4})"
        potential_files = re.findall(file_pattern, result_text)
        
        # Filter to likely file paths
        for file in potential_files:
            if any(ext in file for ext in ['.md', '.png', '.jpg', '.json', '.html']):
                files.append(file)
        
        return list(set(files))  # Remove duplicates
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        if not self.available:
            return []
            
        tools = []
        
        # Define tool categories and descriptions
        tool_definitions = {
            # World tools
            "instantiate_world": {
                "category": "world",
                "description": "Create a new world project with foundation content"
            },
            "list_world_files": {
                "category": "world", 
                "description": "List all files in a world directory"
            },
            
            # Taxonomy tools
            "generate_taxonomy_guidelines": {
                "category": "taxonomy",
                "description": "Generate custom guidelines for a taxonomy type"
            },
            "create_taxonomy_folders": {
                "category": "taxonomy",
                "description": "Create organized categories for your world"
            },
            
            # Entry tools
            "create_world_entry": {
                "category": "entry",
                "description": "Add detailed entries to your world"
            },
            "identify_stub_candidates": {
                "category": "entry",
                "description": "Find entities that need their own entries"
            },
            "create_stub_entries": {
                "category": "entry", 
                "description": "Automatically create placeholder entries"
            },
            
            # Image tools
            "generate_image_from_markdown_file": {
                "category": "image",
                "description": "Create visual representations of your content"
            },
            
            # Site tools  
            "build_static_site": {
                "category": "site",
                "description": "Generate a navigable website from your world"
            }
        }
        
        for tool_name in self.tool_handlers:
            if tool_name in tool_definitions:
                tools.append({
                    "name": tool_name,
                    **tool_definitions[tool_name]
                })
        
        return tools


# Global MCP client instance
mcp_client = MCPClient()

# Export for use in other modules
__all__ = ["mcp_client", "MCPClient"] 