"""
MCP Client for integrating with the Vibe Worldbuilding MCP server.

This module handles communication with the vibe-worldbuilding MCP tools
and provides a clean interface for the FastAPI backend.
"""

import sys
import os
import asyncio
import subprocess
import json
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
    
    # Create empty handlers as fallback
    WORLD_HANDLERS = {}
    TAXONOMY_HANDLERS = {}
    ENTRY_HANDLERS = {}
    IMAGE_HANDLERS = {}
    SITE_HANDLERS = {}

# Define filesystem tools that we'll connect to via the filesystem MCP server
FILESYSTEM_HANDLERS = {
    "read_file": "Read contents of a file",
    "write_file": "Write content to a file", 
    "edit_file": "Edit a file with selective changes",
    "create_directory": "Create a new directory",
    "list_directory": "List contents of a directory",
    "move_file": "Move or rename files and directories",
    "search_files": "Search for files matching a pattern",
    "get_file_info": "Get metadata about a file or directory",
    "list_allowed_directories": "List directories accessible to the filesystem server"
}


class FilesystemMCPClient:
    """Client for communicating with the filesystem MCP server."""
    
    def __init__(self):
        self.filesystem_available = False
        # Set the working directory to allow filesystem access
        self.allowed_directories = [
            str(Path.cwd()),  # Current working directory
            str(Path.cwd().parent),  # Parent directory (for accessing vibe-worldbuilding-mcp)
        ]
        
        try:
            # Test if filesystem MCP server is available by checking npx
            result = subprocess.run([
                "which", "npx"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Test the filesystem server
                test_result = subprocess.run([
                    "npx", "@modelcontextprotocol/server-filesystem", "--version"
                ], capture_output=True, text=True, timeout=10)
                
                if test_result.returncode == 0 or "not found" not in test_result.stderr:
                    self.filesystem_available = True
                    logger.info(f"Filesystem MCP server is available. Allowed directories: {self.allowed_directories}")
                else:
                    logger.warning("Filesystem MCP server package not accessible")
            else:
                logger.warning("npx not available - filesystem tools disabled")
                
        except Exception as e:
            logger.warning(f"Could not test filesystem MCP server: {e}")
    
    async def execute_filesystem_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a filesystem tool using basic file operations."""
        if not self.filesystem_available:
            return {
                "success": False,
                "result": "Filesystem tools are not available",
                "error": "Filesystem MCP server not available"
            }
        
        try:
            # Implement basic filesystem operations directly
            if tool_name == "list_directory":
                return await self._list_directory(parameters)
            elif tool_name == "read_file":
                return await self._read_file(parameters)
            elif tool_name == "write_file":
                return await self._write_file(parameters)
            elif tool_name == "create_directory":
                return await self._create_directory(parameters)
            elif tool_name == "get_file_info":
                return await self._get_file_info(parameters)
            elif tool_name == "search_files":
                return await self._search_files(parameters)
            elif tool_name == "list_allowed_directories":
                return await self._list_allowed_directories(parameters)
            else:
                return {
                    "success": False,
                    "result": f"Filesystem tool {tool_name} not implemented yet",
                    "error": f"Tool {tool_name} not implemented"
                }
                
        except Exception as e:
            logger.error(f"Error executing filesystem tool {tool_name}: {e}")
            return {
                "success": False,
                "result": f"Filesystem tool execution failed: {str(e)}",
                "error": str(e)
            }
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if a path is within allowed directories."""
        try:
            abs_path = Path(path).resolve()
            for allowed in self.allowed_directories:
                if abs_path.is_relative_to(Path(allowed).resolve()):
                    return True
            return False
        except Exception:
            return False
    
    async def _list_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List contents of a directory."""
        path = parameters.get("path", ".")
        
        if not self._is_path_allowed(path):
            return {
                "success": False,
                "result": f"Access denied to path: {path}",
                "error": "Path not in allowed directories"
            }
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {
                    "success": False,
                    "result": f"Directory does not exist: {path}",
                    "error": "Directory not found"
                }
            
            if not path_obj.is_dir():
                return {
                    "success": False,
                    "result": f"Path is not a directory: {path}",
                    "error": "Not a directory"
                }
            
            items = []
            for item in sorted(path_obj.iterdir()):
                if item.is_dir():
                    items.append(f"[DIR] {item.name}")
                else:
                    items.append(f"[FILE] {item.name}")
            
            result = f"Contents of {path}:\n" + "\n".join(items)
            
            return {
                "success": True,
                "result": result,
                "tool_name": "list_directory",
                "parameters": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": f"Error listing directory: {str(e)}",
                "error": str(e)
            }
    
    async def _read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read contents of a file."""
        path = parameters.get("path")
        if not path:
            return {
                "success": False,
                "result": "No path provided",
                "error": "Missing path parameter"
            }
        
        if not self._is_path_allowed(path):
            return {
                "success": False,
                "result": f"Access denied to path: {path}",
                "error": "Path not in allowed directories"
            }
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {
                    "success": False,
                    "result": f"File does not exist: {path}",
                    "error": "File not found"
                }
            
            if not path_obj.is_file():
                return {
                    "success": False,
                    "result": f"Path is not a file: {path}",
                    "error": "Not a file"
                }
            
            content = path_obj.read_text(encoding='utf-8')
            
            return {
                "success": True,
                "result": f"Contents of {path}:\n\n{content}",
                "tool_name": "read_file",
                "parameters": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": f"Error reading file: {str(e)}",
                "error": str(e)
            }
    
    async def _write_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to a file."""
        path = parameters.get("path")
        content = parameters.get("content", "")
        
        if not path:
            return {
                "success": False,
                "result": "No path provided",
                "error": "Missing path parameter"
            }
        
        if not self._is_path_allowed(path):
            return {
                "success": False,
                "result": f"Access denied to path: {path}",
                "error": "Path not in allowed directories"
            }
        
        try:
            path_obj = Path(path)
            # Create parent directories if they don't exist
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            path_obj.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "result": f"Successfully wrote content to {path}",
                "tool_name": "write_file",
                "parameters": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": f"Error writing file: {str(e)}",
                "error": str(e)
            }
    
    async def _create_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a directory."""
        path = parameters.get("path")
        
        if not path:
            return {
                "success": False,
                "result": "No path provided",
                "error": "Missing path parameter"
            }
        
        if not self._is_path_allowed(path):
            return {
                "success": False,
                "result": f"Access denied to path: {path}",
                "error": "Path not in allowed directories"
            }
        
        try:
            path_obj = Path(path)
            path_obj.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "result": f"Successfully created directory: {path}",
                "tool_name": "create_directory",
                "parameters": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": f"Error creating directory: {str(e)}",
                "error": str(e)
            }
    
    async def _get_file_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get file or directory information."""
        path = parameters.get("path")
        
        if not path:
            return {
                "success": False,
                "result": "No path provided",
                "error": "Missing path parameter"
            }
        
        if not self._is_path_allowed(path):
            return {
                "success": False,
                "result": f"Access denied to path: {path}",
                "error": "Path not in allowed directories"
            }
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {
                    "success": False,
                    "result": f"Path does not exist: {path}",
                    "error": "Path not found"
                }
            
            stat = path_obj.stat()
            info = {
                "path": str(path),
                "type": "directory" if path_obj.is_dir() else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:]
            }
            
            result = f"File info for {path}:\n"
            for key, value in info.items():
                result += f"  {key}: {value}\n"
            
            return {
                "success": True,
                "result": result,
                "tool_name": "get_file_info",
                "parameters": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": f"Error getting file info: {str(e)}",
                "error": str(e)
            }
    
    async def _search_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files matching a pattern."""
        path = parameters.get("path", ".")
        pattern = parameters.get("pattern", "*")
        
        if not self._is_path_allowed(path):
            return {
                "success": False,
                "result": f"Access denied to path: {path}",
                "error": "Path not in allowed directories"
            }
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {
                    "success": False,
                    "result": f"Path does not exist: {path}",
                    "error": "Path not found"
                }
            
            matches = []
            if path_obj.is_dir():
                for item in path_obj.rglob(pattern):
                    if self._is_path_allowed(str(item)):
                        matches.append(str(item.relative_to(path_obj)))
            
            result = f"Found {len(matches)} matches for pattern '{pattern}' in {path}:\n"
            for match in sorted(matches[:20]):  # Limit to first 20 results
                result += f"  {match}\n"
            
            if len(matches) > 20:
                result += f"  ... and {len(matches) - 20} more files\n"
            
            return {
                "success": True,
                "result": result,
                "tool_name": "search_files",
                "parameters": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "result": f"Error searching files: {str(e)}",
                "error": str(e)
            }
    
    async def _list_allowed_directories(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List the allowed directories."""
        result = "Allowed directories for filesystem operations:\n"
        for directory in self.allowed_directories:
            result += f"  {directory}\n"
        
        return {
            "success": True,
            "result": result,
            "tool_name": "list_allowed_directories",
            "parameters": parameters
        }


class MCPClient:
    """Client for communicating with MCP servers (worldbuilding + filesystem)."""
    
    def __init__(self):
        self.available = MCP_AVAILABLE
        self.tool_handlers = {}
        self.filesystem_client = FilesystemMCPClient()
        
        if self.available:
            # Combine all worldbuilding tool handlers
            self.tool_handlers.update({
                **WORLD_HANDLERS,
                **TAXONOMY_HANDLERS,
                **ENTRY_HANDLERS,
                **IMAGE_HANDLERS,
                **SITE_HANDLERS,
            })
            
        # Add filesystem tools
        if self.filesystem_client.filesystem_available:
            self.tool_handlers.update(FILESYSTEM_HANDLERS)
            
        total_tools = len(self.tool_handlers)
        logger.info(f"MCP client initialized with {total_tools} tools")
        
        if not self.available and not self.filesystem_client.filesystem_available:
            logger.warning("MCP client initialized without any tools - running in demo mode")
            
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific MCP tool with the given parameters."""
        
        # Check if it's a filesystem tool
        if tool_name in FILESYSTEM_HANDLERS:
            return await self.filesystem_client.execute_filesystem_tool(tool_name, parameters)
            
        # Handle worldbuilding tools
        if not self.available:
            return {
                "success": False,
                "result": "Worldbuilding MCP tools are not available - please check installation",
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
                
                # Check if the result contains error indicators
                is_error = self._is_error_response(text_result)
                
                if is_error:
                    return {
                        "success": False,
                        "result": text_result,
                        "error": text_result,
                        "tool_name": tool_name,
                        "parameters": parameters
                    }
                
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
    
    def _is_error_response(self, result_text: str) -> bool:
        """Check if the result text indicates an error condition."""
        error_indicators = [
            "Error:",
            "error:",
            "failed",
            "Failed",
            "not found",
            "Not found",
            "does not exist",
            "cannot find",
            "Cannot find",
            "Build failed",
            "build failed",
            "Exception:",
            "exception:",
            "Traceback",
            "Invalid",
            "invalid"
        ]
        
        # Check for error indicators at the start of the text (most reliable)
        text_lower = result_text.lower().strip()
        if text_lower.startswith(("error", "failed", "exception", "traceback")):
            return True
            
        # Check for error indicators anywhere in the text
        for indicator in error_indicators:
            if indicator in result_text:
                return True
                
        return False
    
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
            },
            
            # Filesystem tools
            "read_file": {
                "category": "filesystem",
                "description": "Read the contents of a file"
            },
            "write_file": {
                "category": "filesystem",
                "description": "Write content to a file"
            },
            "edit_file": {
                "category": "filesystem",
                "description": "Make selective edits to a file"
            },
            "create_directory": {
                "category": "filesystem",
                "description": "Create a new directory"
            },
            "list_directory": {
                "category": "filesystem",
                "description": "List the contents of a directory"
            },
            "move_file": {
                "category": "filesystem", 
                "description": "Move or rename files and directories"
            },
            "search_files": {
                "category": "filesystem",
                "description": "Search for files matching a pattern"
            },
            "get_file_info": {
                "category": "filesystem",
                "description": "Get metadata about a file or directory"
            },
            "list_allowed_directories": {
                "category": "filesystem",
                "description": "List directories accessible to the filesystem server"
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