import os
import json
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import importlib
import asyncio
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a webhook management assistant that can create and delete webhooks through an MCP server.
Your main tasks are:
1. Create webhooks for specific events or data streams
2. Delete existing webhooks when they are no longer needed
3. Check the webhook history
"""

class WebhookMonitorAgent:
    def __init__(self) -> None:
        try:
            logger.info("Initializing WebhookMonitorAgent...")
            
            # Initialize OpenAI client
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
            
            # Get current MCP server from backend state
            self.mcp = self._get_mcp_server()
            
            # Initialize empty lists
            self.tools = []
            self.openai_tools = []
            
            # Create results directory if it doesn't exist
            self.results_dir = Path("data/webhook_results")
            self.results_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize conversation history with system prompt
            self.conversation_history = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            
        except Exception as e:
            logger.error(f"Failed to initialize WebhookMonitorAgent: {str(e)}")
            raise
            
    def _get_mcp_server(self):
        """Get the current MCP server based on backend state"""
        from backend.routes.mcp import current_mcp_server
        
        module_name = f"agents.utils.mcp_server_{current_mcp_server}"
        try:
            mcp_module = importlib.import_module(module_name)
            return mcp_module.mcp
        except ImportError as e:
            logger.error(f"Failed to import MCP server module: {str(e)}")
            fallback_module = importlib.import_module("agents.utils.mcp_server_nodit")
            return fallback_module.mcp

    async def initialize_tools(self):
        """Async method to initialize webhook-related tools"""
        try:
            # Get all tools and filter for webhook-related ones
            all_tools = await self.mcp.list_tools()
            self.tools = [
                tool for tool in all_tools 
                if any(keyword in tool.name.lower() for keyword in ['webhook', 'hook', 'notification'])
            ]
            
            # Convert MCP tools to OpenAI format
            self.openai_tools = []
            for tool in self.tools:
                logger.info(f"Found webhook tool: {tool.name}")
                self.openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            if not self.openai_tools:
                logger.warning("No webhook-related tools found")
                
        except Exception as e:
            logger.error(f"Failed to initialize webhook tools: {str(e)}")
            raise

    async def execute_tool_by_prompt(self, prompt: str, **kwargs) -> Dict:
        """Execute a webhook-related tool based on the user's prompt"""
        try:
            logger.info(f"Processing webhook prompt: {prompt}")
            
            # Add the prompt to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Get OpenAI's tool selection
            response = self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=self.conversation_history,
                tools=self.openai_tools,
                tool_choice="auto"
            )
            
            # Get the assistant's message
            assistant_message = response.choices[0].message
            
            # Check if OpenAI wants to call any tools
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                # Create a mapping of tool names to their callable functions
                tool_map = {tool.name: tool.fn for tool in self.tools}
                
                results = []
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    logger.info(f"Executing tool: {tool_name}")
                    
                    # Parse the arguments
                    args = json.loads(tool_call.function.arguments)
                    logger.info(f"Tool arguments: {json.dumps(args, indent=2)}")
                    
                    # Call the function
                    if tool_name in tool_map:
                        func = tool_map[tool_name]
                        result = await func(**args) if asyncio.iscoroutinefunction(func) else func(**args)
                        results.append({
                            "tool": tool_name,
                            "result": result
                        })
                    else:
                        logger.error(f"Tool {tool_name} not found")
                
                return {
                    "success": True,
                    "results": results
                }
            
            # If no tools were called, return the assistant's message
            return {
                "success": True,
                "message": assistant_message.content
            }
            
        except Exception as e:
            error_msg = f"Error executing webhook tool: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


