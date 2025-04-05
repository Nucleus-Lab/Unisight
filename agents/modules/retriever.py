import os
import json
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import importlib
import asyncio

from agents.utils.format_utils import format_obj, flatten_json

SYSTEM_PROMPT = """
You are an AI assistant that can interact with blockchain data through an MCP server.
"""

logger = logging.getLogger(__name__)

class MCPRetrieverAgent:
    def __init__(self) -> None:
        try:
            logger.info("Initializing MCPRetrieverAgent...")
            
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
            self.results_dir = Path("data/retriever_results")
            self.results_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize conversation history with system prompt
            self.conversation_history = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            
            # We'll initialize tools in a separate async method
            
        except Exception as e:
            logger.error(f"Failed to initialize MCPRetrieverAgent: {str(e)}")
            raise
            
    def _get_mcp_server(self):
        """Get the current MCP server based on backend state"""
        from backend.routes.mcp import current_mcp_server
        
        # Import the appropriate MCP server module
        module_name = f"agents.utils.mcp_server_{current_mcp_server}"
        try:
            mcp_module = importlib.import_module(module_name)
            return mcp_module.mcp
        except ImportError as e:
            logger.error(f"Failed to import MCP server module: {str(e)}")
            # Fall back to nodit if import fails
            fallback_module = importlib.import_module("agents.utils.mcp_server_nodit")
            return fallback_module.mcp

    async def initialize_tools(self):
        """Async method to initialize tools"""
        try:
            self.tools = await self.mcp.list_tools()
            
            print("tools: ", self.tools)
            
            # Convert MCP tools to OpenAI format
            self.openai_tools = []
            for tool in self.tools:
                logger.info(f"Found tool: {tool.name}")
                self.openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            if not self.openai_tools:
                logger.warning("No suitable tools found for OpenAI to use")
                
        except Exception as e:
            logger.error(f"Failed to initialize tools: {str(e)}")
            raise

    def _generate_filename(self, prompt: str) -> str:
        """Generate a filename based on timestamp and prompt"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create a safe filename from the first 50 chars of the prompt
        safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:50]).rstrip("_")
        return f"{timestamp}_{safe_prompt}.json"

    async def retrieve_by_prompt(self, prompt: str) -> dict:
        """
        Process a prompt, execute tools, and save results to a JSON file
        """
        try:
            logger.info(f"Processing prompt: {prompt}")
            
            # Add user prompt to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Get OpenAI's tool selection
            response = self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=self.conversation_history,
                tools=self.openai_tools,
                tool_choice="auto",
                timeout=30
            )
            
            # Get the assistant's message
            assistant_message = response.choices[0].message
            
            result = None
            
            # Check if OpenAI wants to call any tools
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                # Create a mapping of tool names to their callable functions
                tool_map = {tool.name: tool.fn for tool in self.tools}
                
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    logger.info(f"Executing tool: {tool_name}")
                    
                    # Parse the arguments
                    args = json.loads(tool_call.function.arguments)
                    logger.info(f"Tool arguments: {json.dumps(args, indent=2)}")
                    
                    # Call the function with proper async handling
                    try:
                        if tool_name in tool_map:
                            func = tool_map[tool_name]
                            # Check if the function is async
                            if asyncio.iscoroutinefunction(func):
                                result = await func(**args)
                            else:
                                result = func(**args)
                            logger.info(f"Tool execution successful: {tool_name}")
                            
                            # TODO: double check this again
                            # Format and flatten each item
                            flattened_items = []
                            for item in result:
                                formatted_item = format_obj(item)
                                flattened_item = flatten_json(formatted_item)
                                flattened_items.append(flattened_item)
                            
                            result = flattened_items
                        else:
                            error_msg = f"Tool {tool_name} not found in available tools"
                            logger.error(error_msg)
                            raise ValueError(error_msg)
                    except Exception as e:
                        error_msg = f"Error executing tool {tool_name}: {str(e)}"
                        logger.error(error_msg)
                        raise
            
            # Generate filename and save results
            filename = self._generate_filename(prompt)
            file_path = self.results_dir / filename
            
            # Save results to JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Result saved to {file_path}")
            
            return {
                "success": True,
                "file_path": str(file_path)
            }
            
        except Exception as e:
            error_msg = f"Error in retrieve_by_prompt: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
