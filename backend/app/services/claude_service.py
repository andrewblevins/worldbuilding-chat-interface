"""
Claude AI service for handling chat responses and worldbuilding interactions.
"""

import json
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from loguru import logger

from ..core.config import settings
from ..core.mcp_client import mcp_client


class ClaudeService:
    """Service for interacting with Claude AI for worldbuilding chat."""
    
    def __init__(self):
        self.client = None
        self.available = False
        
        if settings.ANTHROPIC_API_KEY:
            try:
                self.client = Anthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    default_headers={
                        "anthropic-beta": "interleaved-thinking-2025-05-14"  # Enable thinking
                    }
                )
                self.available = True
                logger.info("Claude service initialized successfully with thinking support")
            except Exception as e:
                logger.error(f"Failed to initialize Claude service: {e}")
                self.available = False
        else:
            logger.warning("No Anthropic API key provided - Claude service unavailable")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Claude with available worldbuilding tools."""
        available_tools = mcp_client.get_available_tools() if mcp_client.available else []
        
        tools_description = "**Available Tools:**\n"
        if available_tools:
            for tool in available_tools:
                tools_description += f"- **{tool['name']}** ({tool['category']}): {tool['description']}\n"
        else:
            tools_description += "- No MCP tools available (running in demo mode)\n"

        system_prompt = f"""You are a helpful AI assistant specializing in worldbuilding and creative writing. You have access to powerful worldbuilding tools through the MCP (Model Context Protocol) system.

{tools_description}

**Your Role:**
- Help users create detailed, immersive fictional worlds
- Use the available MCP tools actively to generate content, organize information, and create visual elements
- Provide guidance on worldbuilding concepts like cultures, magic systems, geography, history, etc.
- Be creative and inspire users to develop rich, cohesive worlds

**Tool Usage Guidelines:**
- When users ask to create worlds, use `instantiate_world` with a descriptive world name and rich content
- For organizing content, use taxonomy tools like `create_taxonomy` or `create_taxonomy_with_llm_guidelines`
- For detailed content, use `create_world_entry` (this automatically creates stub entries for referenced entities)
- For visuals, use `generate_image_from_markdown_file` after creating content
- For building websites, use `build_static_site` to create navigable sites
- Always explain what tools you're using and why

**Response Style:**
- Be enthusiastic and encouraging about worldbuilding
- Provide concrete, actionable suggestions
- Ask follow-up questions to develop ideas further
- Explain worldbuilding concepts when helpful
- When using tools, explain the results and suggest next steps

Remember: You have real tools at your disposal - use them actively to help users build amazing worlds!"""
        
        return system_prompt
    
    def _get_claude_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tools formatted for Claude's tool calling API."""
        if not mcp_client.available:
            return []
        
        claude_tools = []
        available_tools = mcp_client.get_available_tools()
        
        # Define tool schemas for Claude
        tool_schemas = {
            "instantiate_world": {
                "name": "instantiate_world",
                "description": "Create a new world project with foundation content and directory structure",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "world_name": {
                            "type": "string",
                            "description": "Name of the world (used for directory naming)"
                        },
                        "world_content": {
                            "type": "string", 
                            "description": "Rich world overview/foundation content with concepts, atmosphere, key elements"
                        },
                        "taxonomies": {
                            "type": "array",
                            "description": "List of initial taxonomy categories (e.g., characters, locations, artifacts)",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"}
                                },
                                "required": ["name", "description"]
                            },
                            "default": []
                        },
                        "base_directory": {
                            "type": "string",
                            "description": "Base directory for world creation",
                            "default": "."
                        }
                    },
                    "required": ["world_name", "world_content"]
                }
            },
            "create_taxonomy": {
                "name": "create_taxonomy",
                "description": "Create organized category folders for your world",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "world_directory": {
                            "type": "string",
                            "description": "Path to the world directory"
                        },
                        "taxonomy_name": {
                            "type": "string",
                            "description": "Name of the taxonomy (e.g., characters, locations, artifacts)"
                        },
                        "taxonomy_description": {
                            "type": "string",
                            "description": "Description of what this taxonomy contains"
                        }
                    },
                    "required": ["world_directory", "taxonomy_name", "taxonomy_description"]
                }
            },
            "create_world_entry": {
                "name": "create_world_entry", 
                "description": "Add detailed entries to your world with automatic stub generation for referenced entities",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "world_directory": {
                            "type": "string",
                            "description": "Path to the world directory"
                        },
                        "taxonomy": {
                            "type": "string",
                            "description": "Taxonomy category for this entry"
                        },
                        "entry_name": {
                            "type": "string",
                            "description": "Name of the entry"
                        },
                        "entry_content": {
                            "type": "string",
                            "description": "Detailed content for the entry"
                        }
                    },
                    "required": ["world_directory", "taxonomy", "entry_name", "entry_content"]
                }
            },
            "generate_image_from_markdown_file": {
                "name": "generate_image_from_markdown_file",
                "description": "Create visual representations of your content from markdown files",
                "input_schema": {
                    "type": "object", 
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the markdown file to generate image for"
                        },
                        "style": {
                            "type": "string",
                            "description": "Art style for the image",
                            "default": "fantasy illustration"
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "description": "Image aspect ratio",
                            "enum": ["1:1", "16:9", "9:16", "3:4", "4:3"],
                            "default": "16:9"
                        }
                    },
                    "required": ["filepath"]
                }
            },
            "build_static_site": {
                "name": "build_static_site",
                "description": "Generate a navigable website from your world content",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "world_directory": {
                            "type": "string",
                            "description": "Path to the world directory"
                        },
                        "action": {
                            "type": "string",
                            "description": "Build action to perform",
                            "enum": ["build", "dev", "preview"],
                            "default": "build"
                        }
                    },
                    "required": ["world_directory"]
                }
            }
        }
        
        # Only include tools that are actually available
        for tool in available_tools:
            tool_name = tool["name"]
            if tool_name in tool_schemas:
                claude_tools.append(tool_schemas[tool_name])
        
        return claude_tools
    
    async def generate_response(self, message: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response using Claude AI with tool calling support.
        
        Args:
            message: The user's message
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with response content and metadata
        """
        if not self.available:
            return {
                "content": "Claude AI service is not available. Please check the API key configuration.",
                "role": "assistant",
                "tool_calls": [],
                "files_created": [],
                "error": "Claude service unavailable"
            }
        
        try:
            # Prepare conversation history
            messages = []
            if conversation_history:
                # Process conversation history to handle content blocks properly
                for msg in conversation_history:
                    if isinstance(msg.get("content"), list):
                        # Content blocks format - preserve as-is
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    else:
                        # Simple string content
                        messages.append({
                            "role": msg["role"], 
                            "content": msg["content"]
                        })
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Get available tools for Claude
            tools = self._get_claude_tools()
            
            # Call Claude API with tools and thinking
            if tools:
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",  # Claude Sonnet 4
                    max_tokens=2048,
                    temperature=1.0,  # Required when thinking is enabled
                    system=self.get_system_prompt(),
                    messages=messages,
                    tools=tools,
                    thinking={"type": "enabled", "budget_tokens": 10000}
                )
            else:
                # No tools available, use basic chat
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",  # Claude Sonnet 4
                    max_tokens=2048,
                    temperature=1.0,  # Required when thinking is enabled
                    system=self.get_system_prompt(),
                    messages=messages,
                    thinking={"type": "enabled", "budget_tokens": 10000}
                )
            
            # Extract response content, thinking, and tool calls
            response_content = ""
            thinking_content = ""
            tool_calls = []
            content_blocks = []
            
            if response.content:
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        response_content += content_block.text
                        content_blocks.append({
                            "type": "text",
                            "text": content_block.text
                        })
                    elif hasattr(content_block, 'type') and content_block.type == 'thinking':
                        # ThinkingBlock uses 'thinking' attribute, not 'content'
                        thinking_content += content_block.thinking
                        content_blocks.append({
                            "type": "thinking", 
                            "thinking": content_block.thinking
                        })
                    elif hasattr(content_block, 'type') and content_block.type == 'tool_use':
                        tool_calls.append({
                            "tool_id": content_block.id,
                            "tool_name": content_block.name,
                            "tool_input": content_block.input,
                            "status": "pending"
                        })
                        content_blocks.append({
                            "type": "tool_use",
                            "id": content_block.id,
                            "name": content_block.name,
                            "input": content_block.input
                        })
            
            return {
                "content": response_content,
                "thinking": thinking_content,
                "content_blocks": content_blocks,  # Preserve for conversation history
                "role": "assistant", 
                "tool_calls": tool_calls,
                "files_created": [],
                "model": "claude-sonnet-4-20250514",
                "usage": {
                    "input_tokens": response.usage.input_tokens if hasattr(response, 'usage') else 0,
                    "output_tokens": response.usage.output_tokens if hasattr(response, 'usage') else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            return {
                "content": f"I encountered an error while processing your request: {str(e)}",
                "role": "assistant",
                "tool_calls": [],
                "files_created": [],
                "error": str(e)
            }
    
    async def process_with_tools(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a message and execute any tools that Claude requests.
        
        Args:
            message: The user's message
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with response and any tool execution results
        """
        # Get Claude's response with potential tool calls
        response = await self.generate_response(message, conversation_history)
        
        # If Claude requested tools and MCP is available, execute them
        if response.get("tool_calls") and mcp_client.available:
            executed_tools = []
            files_created = []
            tool_results = []
            
            for tool_call in response["tool_calls"]:
                try:
                    tool_name = tool_call["tool_name"]
                    tool_input = tool_call["tool_input"]
                    tool_id = tool_call["tool_id"]
                    
                    logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
                    
                    # Execute the tool through MCP
                    tool_result = await mcp_client.execute_tool(tool_name, tool_input)
                    
                    if tool_result.get("success"):
                        executed_tools.append({
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "tool_input": tool_input,
                            "result": tool_result["result"],
                            "status": "completed"
                        })
                        
                        # Track files created
                        if tool_result.get("files_created"):
                            files_created.extend(tool_result["files_created"])
                            
                        # Prepare tool result for Claude's follow-up
                        tool_results.append({
                            "tool_use_id": tool_id,
                            "type": "tool_result",
                            "content": tool_result["result"]
                        })
                    else:
                        executed_tools.append({
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "tool_input": tool_input,
                            "error": tool_result.get("error", "Unknown error"),
                            "status": "failed"
                        })
                        
                        # Include error in tool results
                        tool_results.append({
                            "tool_use_id": tool_id,
                            "type": "tool_result",
                            "content": f"Error: {tool_result.get('error', 'Unknown error')}",
                            "is_error": True
                        })
                        
                except Exception as e:
                    logger.error(f"Error executing tool {tool_call['tool_name']}: {e}")
                    executed_tools.append({
                        "tool_id": tool_call.get("tool_id", "unknown"),
                        "tool_name": tool_call["tool_name"],
                        "error": str(e),
                        "status": "failed"
                    })
            
            # Update response with execution results
            response["tool_calls"] = executed_tools
            response["files_created"] = files_created
            
            # If tools were executed, get Claude's follow-up response
            if tool_results:
                try:
                    # Prepare messages with tool results
                    follow_up_messages = conversation_history or []
                    follow_up_messages.append({"role": "user", "content": message})
                    follow_up_messages.append({
                        "role": "assistant", 
                        "content": response.get("content", "")
                    })
                    
                    # Add tool results
                    for tool_result in tool_results:
                        follow_up_messages.append({
                            "role": "user",
                            "content": tool_result["content"]
                        })
                    
                    # Get Claude's follow-up response
                    follow_up = self.client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        temperature=1.0,  # Required when thinking is enabled
                        system=self.get_system_prompt(),
                        messages=follow_up_messages,
                        thinking={"type": "enabled", "budget_tokens": 5000}
                    )
                    
                    # Add follow-up content to response
                    if follow_up.content:
                        follow_up_text = ""
                        for content_block in follow_up.content:
                            if hasattr(content_block, 'text'):
                                follow_up_text += content_block.text
                        
                        if follow_up_text.strip():
                            response["content"] += f"\n\n{follow_up_text}"
                    
                except Exception as e:
                    logger.error(f"Error getting Claude follow-up: {e}")
                    # Add basic tool summary if follow-up fails
                    completed_tools = [t["tool_name"] for t in executed_tools if t["status"] == "completed"]
                    if completed_tools:
                        response["content"] += f"\n\n✅ Successfully executed: {', '.join(completed_tools)}"
                        if files_created:
                            response["content"] += f"\n📁 Created {len(files_created)} files"
        
        return response


# Create a global instance
claude_service = ClaudeService() 