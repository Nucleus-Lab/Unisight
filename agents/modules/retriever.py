import os
import json
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from agents.utils.mcp_client import MCPClient

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
            
            # Connect to the MCP server
            self.mcp_client = MCPClient()
            self.tools = self.mcp_client.connect_to_server("agents/utils/mcp_server.py")
            logger.info(f"Successfully connected to MCP server. Found {len(self.tools)} tools.")
            
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
            
            # Initialize conversation history with system prompt
            self.conversation_history = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            
            # Create results directory if it doesn't exist
            self.results_dir = Path("data/retriever_results")
            self.results_dir.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            logger.error(f"Failed to initialize MCPRetrieverAgent: {str(e)}")
            raise

    def _generate_filename(self, prompt: str) -> str:
        """Generate a filename based on timestamp and prompt"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create a safe filename from the first 50 chars of the prompt
        safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:50]).rstrip("_")
        return f"{timestamp}_{safe_prompt}.json"

    def retrieve_by_prompt(self, prompt: str) -> dict:
        """
        Process a prompt, execute tools, and save results to a JSON file
        
        Args:
            prompt (str): The user's prompt/question
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the operation was successful
                - file_path (str): Path to the saved JSON file (if successful)
                - error (str): Error message (if not successful)
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
            
            # Initialize results dictionary
            results = {
                "prompt": prompt,
                "timestamp": datetime.now().isoformat(),
                "tools_results": {}
            }
            
            # Check if OpenAI wants to call any tools
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    logger.info(f"Executing tool: {tool_name}")
                    
                    # Parse the arguments
                    args = json.loads(tool_call.function.arguments)
                    logger.info(f"Tool arguments: {json.dumps(args, indent=2)}")
                    
                    # Call the tool
                    try:
                        result = self.mcp_client.call_tool(tool_name, args)
                        
                        # Parse the result
                        if isinstance(result, str):
                            try:
                                result_data = json.loads(result)
                            except json.JSONDecodeError:
                                result_data = {"raw_result": result}
                        else:
                            # Handle non-string results
                            if hasattr(result, 'text'):
                                try:
                                    result_data = json.loads(result.text)
                                except json.JSONDecodeError:
                                    result_data = {"text": result.text}
                            elif hasattr(result, '__dict__'):
                                result_data = result.__dict__
                            else:
                                result_data = {"result": str(result)}
                        
                        # Store the result
                        results["tools_results"][tool_name] = {
                            "arguments": args,
                            "result": result_data
                        }
                        logger.info(f"Tool {tool_name} executed successfully")
                        
                    except Exception as e:
                        error_msg = f"Error executing tool {tool_name}: {str(e)}"
                        logger.error(error_msg)
                        results["tools_results"][tool_name] = {
                            "arguments": args,
                            "error": error_msg
                        }
            
            # Generate filename and save results
            filename = self._generate_filename(prompt)
            file_path = self.results_dir / filename
            
            # Save results to JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {file_path}")
            
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

    def close(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'mcp_client'):
                self.mcp_client.close()
                logger.info("MCPRetrieverAgent closed successfully")
        except Exception as e:
            logger.error(f"Error closing MCPRetrieverAgent: {str(e)}")
