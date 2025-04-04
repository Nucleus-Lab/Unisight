import sys
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.session = None
        self.server_process = None
        self.exit_stack = None
        self._event_loop = None

    def _get_event_loop(self):
        """Get or create an event loop"""
        if self._event_loop is None or self._event_loop.is_closed():
            try:
                self._event_loop = asyncio.get_event_loop()
            except RuntimeError:
                self._event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._event_loop)
        return self._event_loop

    def connect_to_server(self, server_script_path):
        """Connect to an MCP server synchronously"""
        logger.info(f"Starting MCP server from {server_script_path}...")
        
        async def _connect():
            try:
                # Set up the server parameters for stdio communication
                server_params = StdioServerParameters(
                    command=sys.executable,
                    args=[server_script_path],
                    env=None
                )
                
                # Create a client connection to the MCP server
                self.exit_stack = AsyncExitStack()
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                stdio, write = stdio_transport
                
                # Initialize the MCP client session
                self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
                await self.session.initialize()
                
                # List available tools
                response = await self.session.list_tools()
                tools = response.tools
                logger.info(f"Connected to server with tools: {[tool.name for tool in tools]}")
                
                return tools
            except Exception as e:
                logger.error(f"Error connecting to MCP server: {str(e)}")
                if self.exit_stack:
                    await self.exit_stack.aclose()
                raise

        loop = self._get_event_loop()
        try:
            return loop.run_until_complete(_connect())
        except Exception as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            raise

    def call_tool(self, tool_name, tool_args):
        """Call a tool on the MCP server synchronously"""
        logger.info(f"Calling MCP tool '{tool_name}' with args: {json.dumps(tool_args, indent=2)}")
        
        async def _call_tool():
            try:
                result = await self.session.call_tool(tool_name, tool_args)
                logger.info(f"Tool result: {result.content}")
                return result.content
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {str(e)}")
                raise

        return self._event_loop.run_until_complete(_call_tool())
    
    def close(self):
        """Close the MCP client connection synchronously"""
        logger.info("Closing MCP client connection...")
        
        async def _close():
            try:
                if self.exit_stack:
                    await self.exit_stack.aclose()
                    logger.info("MCP client connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing MCP client connection: {str(e)}")
                raise

        if self._event_loop and not self._event_loop.is_closed():
            try:
                self._event_loop.run_until_complete(_close())
            finally:
                self._event_loop.close()