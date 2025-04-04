import os
import json
import asyncio
import subprocess
import sys
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

async def test_mcp_server():
    """Test the MCP server directly without OpenAI integration"""
    print("Testing MCP server...")
    
    # Start the MCP server as a subprocess
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
    print(f"Starting MCP server from {server_path}...")
    
    # Start server process
    server_process = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Give the server a moment to start up
    await asyncio.sleep(1)
    
    # Check if the server process is still running
    if server_process.poll() is not None:
        # Process has terminated, get error output
        _, stderr = server_process.communicate()
        print(f"Server failed to start. Error: {stderr}")
        return
    
    try:
        # Set up exit stack for resource management
        async with AsyncExitStack() as exit_stack:
            # Set up server parameters
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[server_path],
                env=None
            )
            
            print("Connecting to MCP server...")
            # Connect to the MCP server
            try:
                stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
                stdio, write = stdio_transport
            except Exception as e:
                print(f"Failed to connect to MCP server: {str(e)}")
                return
            
            # Create a session
            try:
                session = await exit_stack.enter_async_context(ClientSession(stdio, write))
                print("Session established successfully")
            except Exception as e:
                print(f"Failed to create MCP session: {str(e)}")
                return
            
            # List available tools
            print("Listing available tools...")
            try:
                response = await session.list_tools()
                tools = response.tools
                print(f"Available tools: {[tool.name for tool in tools]}")
            except Exception as e:
                print(f"Failed to list tools: {str(e)}")
                return
            # Test the get_token_holders_by_contract tool
            if any(tool.name == "get_token_holders_by_contract" for tool in tools):
                print("\nTesting get_token_holders_by_contract tool...")
                # USDC on Ethereum
                token_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
                
                args = {
                    "blockchain": "ethereum",
                    "network": "mainnet",
                    "contractAddress": token_address,
                    "page": 1,
                    "limit": 5
                }
                
                print(f"Calling get_token_holders_by_contract with args: {json.dumps(args, indent=2)}")
                try:
                    result = await session.call_tool("get_token_holders_by_contract", args)
                    
                    print("\nTool result:")
                    if isinstance(result.content, str):
                        try:
                            # Try to parse as JSON for better formatting
                            parsed_result = json.loads(result.content)
                            print(json.dumps(parsed_result, indent=2))
                        except json.JSONDecodeError:
                            # If not JSON, print as is
                            print(result.content)
                    else:
                        print(result.content)
                except Exception as e:
                    print(f"Error calling tool: {str(e)}")
            else:
                print("Tool get_token_holders_by_contract not found")
    finally:
        # Terminate the server process if it's still running
        if server_process and server_process.poll() is None:
            print("\nShutting down MCP server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
