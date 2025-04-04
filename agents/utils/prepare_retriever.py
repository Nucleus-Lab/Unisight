import os
import json
import dspy
from agents.utils.mcp_client import MCPClient
import logging

logger = logging.getLogger(__name__)

def get_lm_for_retriever():
    try:
        mcp_client = MCPClient()
        tools = mcp_client.connect_to_server("agents/utils/mcp_server.py")
            
        # Convert MCP tools to OpenAI tool format and ensure they're JSON serializable
        openai_tools = []
        for tool in tools:
            logger.info(f"Found tool: {tool.name}")
            # Convert the input schema to a proper dictionary if it isn't already
            if isinstance(tool.inputSchema, str):
                try:
                    input_schema = json.loads(tool.inputSchema)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse input schema for {tool.name}, using empty schema")
                    input_schema = {}
            else:
                input_schema = tool.inputSchema

            tool_spec = {
                "type": "function",
                "function": {
                    "name": str(tool.name),
                    "description": str(tool.description),
                    "parameters": dict(input_schema)  # Ensure it's a plain dict
                }
            }
            openai_tools.append(tool_spec)

        if not openai_tools:
            logger.warning("No suitable tools found for OpenAI to use")

        # Configure dspy with basic settings first
        lm = dspy.LM(
            model=os.getenv("MODEL_NAME"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_BASE_URL")
        )
        
        # Then set the tools separately to avoid serialization issues
        lm.tools = openai_tools
        
        return lm
    except Exception as e:
        logger.error(f"Error initializing LM: {str(e)}")
        raise
