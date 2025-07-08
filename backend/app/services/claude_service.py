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
                self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.available = True
                logger.info("Claude service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude service: {e}")
                self.available = False
        else:
            logger.warning("No Anthropic API key provided - Claude service unavailable")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Claude with available worldbuilding tools."""
        available_tools = mcp_client.get_available_tools() if mcp_client.available else {}
        
        system_prompt = f"""You are a helpful AI assistant specializing in worldbuilding and creative writing. You have access to powerful worldbuilding tools through the MCP (Model Context Protocol) system.

**Available Tools:**
{json.dumps(available_tools, indent=2)}

**Your Role:**
- Help users create detailed, immersive fictional worlds
- Use the available MCP tools to generate content, organize information, and create visual elements
- Provide guidance on worldbuilding concepts like cultures, magic systems, geography, history, etc.
- Be creative and inspire users to develop rich, cohesive worlds

**Tool Usage Guidelines:**
- When users ask to create worlds, use `instantiate_world` 
- For organizing content, use taxonomy tools like `create_taxonomy_folders`
- For detailed content, use `create_world_entry`
- For visuals, use `generate_image_from_markdown_file`
- Always explain what tools you're using and why

**Response Style:**
- Be enthusiastic and encouraging about worldbuilding
- Provide concrete, actionable suggestions
- Ask follow-up questions to develop ideas further
- Explain worldbuilding concepts when helpful

Remember: You have real tools at your disposal - use them actively to help users build amazing worlds!"""
        
        return system_prompt
    
    async def generate_response(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate a response using Claude AI.
        
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
                messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Claude Sonnet 3.5
                max_tokens=2048,
                temperature=0.7,
                system=self.get_system_prompt(),
                messages=messages
            )
            
            # Extract response content
            response_content = ""
            if response.content:
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        response_content += content_block.text
            
            # Check if Claude mentioned any tools that we should execute
            tool_calls = []
            files_created = []
            
            # Simple tool detection - look for tool mentions in response
            if "instantiate_world" in response_content.lower():
                # Extract world creation parameters from the response
                # This is a simplified approach - in a full implementation, 
                # you'd want more sophisticated parameter extraction
                tool_calls.append({
                    "tool": "instantiate_world",
                    "params": {"name": "generated-world", "description": "AI-generated world"},
                    "status": "pending"
                })
            
            return {
                "content": response_content,
                "role": "assistant", 
                "tool_calls": tool_calls,
                "files_created": files_created,
                "model": "claude-3-5-sonnet-20241022",
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
    
    async def process_with_tools(self, message: str) -> Dict[str, Any]:
        """
        Process a message and potentially execute MCP tools based on Claude's response.
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary with response and any tool execution results
        """
        # Get Claude's response
        response = await self.generate_response(message)
        
        # If Claude suggested tools and MCP is available, execute them
        if response.get("tool_calls") and mcp_client.available:
            executed_tools = []
            files_created = []
            
            for tool_call in response["tool_calls"]:
                try:
                    tool_name = tool_call["tool"]
                    tool_params = tool_call["params"]
                    
                    # Execute the tool through MCP
                    tool_result = await mcp_client.execute_tool(tool_name, tool_params)
                    
                    if tool_result.get("success"):
                        executed_tools.append({
                            "tool": tool_name,
                            "params": tool_params,
                            "result": tool_result,
                            "status": "completed"
                        })
                        
                        # Track files created
                        if tool_result.get("files_created"):
                            files_created.extend(tool_result["files_created"])
                    else:
                        executed_tools.append({
                            "tool": tool_name,
                            "params": tool_params,
                            "error": tool_result.get("error", "Unknown error"),
                            "status": "failed"
                        })
                        
                except Exception as e:
                    logger.error(f"Error executing tool {tool_call['tool']}: {e}")
                    executed_tools.append({
                        "tool": tool_call["tool"],
                        "error": str(e),
                        "status": "failed"
                    })
            
            # Update response with execution results
            response["tool_calls"] = executed_tools
            response["files_created"] = files_created
            
            # If tools were executed successfully, mention it in the response
            if executed_tools:
                tool_summary = ", ".join([t["tool"] for t in executed_tools if t["status"] == "completed"])
                if tool_summary:
                    response["content"] += f"\n\n✅ I've executed these tools for you: {tool_summary}"
                    if files_created:
                        response["content"] += f"\n📁 Created {len(files_created)} files"
        
        return response


# Create singleton instance
claude_service = ClaudeService() 