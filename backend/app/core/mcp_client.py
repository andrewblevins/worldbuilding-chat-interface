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
MCP_PATH = Path(__file__).parent.parent.parent.parent.parent / "vibe-worldbuilding-mcp"
if MCP_PATH.exists():
    sys.path.insert(0, str(MCP_PATH))
else:
    logger.warning(f"MCP path not found at: {MCP_PATH}")

try:
    # Import MCP tool handlers
    from vibe_worldbuilding.tools.world import handle_world_tool, WORLD_HANDLERS
    from vibe_worldbuilding.tools.taxonomy import handle_taxonomy_tool, TAXONOMY_HANDLERS  
    from vibe_worldbuilding.tools.entries import handle_entry_tool, ENTRY_HANDLERS
    from vibe_worldbuilding.tools.images import handle_image_tool, IMAGE_HANDLERS
    from vibe_worldbuilding.tools.site import handle_site_tool, SITE_HANDLERS
    MCP_AVAILABLE = True
    logger.info("Successfully imported vibe-worldbuilding MCP tools")
    total_tools = len(WORLD_HANDLERS) + len(TAXONOMY_HANDLERS) + len(ENTRY_HANDLERS) + len(IMAGE_HANDLERS) + len(SITE_HANDLERS)
    logger.info(f"Available tools: {total_tools} tools loaded")
except ImportError as e:
    logger.warning(f"Could not import MCP tools: {e}")
    MCP_AVAILABLE = False
    # Define empty handlers for graceful degradation
    WORLD_HANDLERS = {}
    TAXONOMY_HANDLERS = {}
    ENTRY_HANDLERS = {}
    IMAGE_HANDLERS = {}
    SITE_HANDLERS = {}


class MCPClient:
    """Client for communicating with the Vibe Worldbuilding MCP server."""
    
    def __init__(self):
        self.available = MCP_AVAILABLE
        self.tool_handlers = {}
        
        if self.available:
            # Combine all tool handlers
            self.tool_handlers.update({
                **WORLD_HANDLERS,
                **TAXONOMY_HANDLERS,
                **ENTRY_HANDLERS,
                **IMAGE_HANDLERS,
                **SITE_HANDLERS,
            })
            logger.info(f"MCP client initialized with {len(self.tool_handlers)} tools")
        else:
            logger.warning("MCP client initialized without tools - running in demo mode")
            
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific MCP tool with the given parameters."""
        if not self.available:
            return {
                "success": False,
                "result": "MCP tools are not available - please check installation",
                "error": "MCP not available",
                "tool_name": tool_name,
                "parameters": parameters
            }
            
        if tool_name not in self.tool_handlers:
            return {
                "success": False,
                "result": f"Unknown tool: {tool_name}. Available tools: {', '.join(self.tool_handlers.keys())}",
                "error": f"Tool {tool_name} not found",
                "tool_name": tool_name,
                "parameters": parameters
            }
            
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
                return {
                    "success": False,
                    "result": f"No handler found for tool: {tool_name}",
                    "error": f"Handler not found for {tool_name}",
                    "tool_name": tool_name,
                    "parameters": parameters
                }
                
            # Convert MCP result to our format
            if isinstance(result, list) and len(result) > 0:
                # MCP returns a list of TextContent objects
                text_result = result[0].text if hasattr(result[0], 'text') else str(result[0])
                
                # Extract file information from the result
                files_created = self._extract_files_from_result(text_result)
                
                return {
                    "success": True,
                    "result": text_result,
                    "files_created": files_created,
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
        
        # Pattern for "Generated: path/to/file"
        generated_pattern = r"[Gg]enerated[:\s]+([^\s\n]+)"
        files.extend(re.findall(generated_pattern, result_text))
        
        # Pattern for file paths in general (*.md, *.png, etc.)
        file_pattern = r"([^\s]+\.[a-zA-Z]{2,4})"
        potential_files = re.findall(file_pattern, result_text)
        
        # Filter to likely file paths
        for file in potential_files:
            if any(ext in file for ext in ['.md', '.png', '.jpg', '.json', '.html', '.txt']):
                files.append(file)
        
        return list(set(files))  # Remove duplicates
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools with descriptions."""
        if not self.available:
            return []
            
        tools = []
        
        # Define tool categories and descriptions
        tool_definitions = {
            # World tools
            "instantiate_world": {
                "category": "world",
                "description": "Create a new world project with foundation content and directory structure"
            },
            
            # Taxonomy tools
            "create_taxonomy": {
                "category": "taxonomy",
                "description": "Create organized category folders for your world"
            },
            "create_taxonomy_with_llm_guidelines": {
                "category": "taxonomy",
                "description": "Create taxonomy with AI-generated custom guidelines"
            },
            
            # Entry tools
            "create_world_entry": {
                "category": "entry",
                "description": "Add detailed entries to your world with auto-stub generation"
            },
            "create_stub_entries": {
                "category": "entry", 
                "description": "Create placeholder entries for referenced entities"
            },
            "generate_entry_descriptions": {
                "category": "entry",
                "description": "Generate descriptions for multiple entries"
            },
            "add_entry_frontmatter": {
                "category": "entry",
                "description": "Add metadata frontmatter to entries"
            },
            "analyze_world_consistency": {
                "category": "entry",
                "description": "Check your world for logical consistency and coherence"
            },
            
            # Image tools
            "generate_image_from_markdown_file": {
                "category": "image",
                "description": "Create visual representations of your content"
            },
            "generate_image_prompt_for_entry": {
                "category": "image",
                "description": "Generate optimized image prompts for entries"
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

    def get_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific tool by name."""
        available_tools = self.get_available_tools()
        for tool in available_tools:
            if tool["name"] == tool_name:
                return tool
        return None


# Create a global instance
mcp_client = MCPClient() 