import os
import json
import subprocess
import time
import asyncio
import requests
import argparse
from contextlib import AsyncExitStack
from openai import OpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys
from prompts.prompt import SYSTEM_PROMPT

import json

# 解析命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='Test MCP server with OpenAI')
    parser.add_argument('--server', type=str, default='mcp_server.py',
                        help='MCP server script path (default: mcp_server.py)')
    parser.add_argument('--address', type=str, 
                        default='0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
                        help='Example blockchain address to use in tests')
    parser.add_argument('--model', type=str, default='gpt-4o',
                        help='OpenAI model to use (default: gpt-4o)')
    return parser.parse_args()

# Load environment variables
load_dotenv()

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # If not in .env, prompt the user
    OPENAI_API_KEY = input("Please enter your OpenAI API key: ")
    # Save it for future use
    with open(".env", "a") as f:
        f.write(f"\nOPENAI_API_KEY=\"{OPENAI_API_KEY}\"\n")

# 从环境变量获取模型名称，如果没有则使用默认值
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class MCPClient:
    def __init__(self):
        self.session = None
        self.server_process = None
        self.exit_stack = None

    async def connect_to_server(self, server_script_path):
        """Connect to an MCP server"""
        print(f"Starting MCP server from {server_script_path}...")
        
        # Set up the server parameters for stdio communication
        server_params = StdioServerParameters(
            command=sys.executable,  # 使用当前 Python 解释器
            args=[server_script_path],
            env=None
        )
        
        # Create a client connection to the MCP server using async context manager properly
        self.exit_stack = AsyncExitStack()
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        
        # Initialize the MCP client session
        self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        # 初始化会话 - 这一步是必要的！
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        
        return tools

    async def call_tool(self, tool_name, tool_args):
        """Call a tool on the MCP server"""
        print(f"\nCalling MCP tool '{tool_name}' with args: {json.dumps(tool_args, indent=2)}")
        
        # Make the actual tool call through the MCP protocol
        result = await self.session.call_tool(tool_name, tool_args)
        
        # Print the result
        print(f"\nTool result: {result}")
        
        return result
    
    async def close(self):
        """Close the MCP client connection"""
        print("Closing MCP client connection...")
        try:
            if self.exit_stack:
                await self.exit_stack.aclose()
                print("MCP client connection closed successfully")
        except Exception as e:
            print(f"Error closing MCP client connection: {str(e)}")

async def test_with_openai():
    """Test the MCP server using OpenAI"""
    # 解析命令行参数
    args = parse_arguments()
    
    print("Testing MCP server with OpenAI...")
    print(f"Using server script: {args.server}")
    print(f"Using example address: {args.address}")
    print(f"Using OpenAI model: {args.model}")
    
    # 保存模型名称为局部变量，确保在整个函数中可用
    model_name = args.model
    
    # Example blockchain address
    example_address = args.address
    
    # Connect to the MCP server
    try:
        print("Connecting to MCP server...")
        mcp_client = MCPClient()
        tools = await mcp_client.connect_to_server(args.server)
        print(f"Successfully connected to MCP server. Found {len(tools)} tools.")
    except Exception as e:
        print(f"Failed to connect to MCP server: {str(e)}")
        raise
    
    # Convert MCP tools to OpenAI tool format
    # 将所有工具添加到 OpenAI 工具列表
    openai_tools = []
    for tool in tools:
        print(f"Found tool: {tool.name}")
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })
    
    if not openai_tools:
        print("Warning: No suitable tools found for OpenAI to use")
    
    # Prepare a prompt for OpenAI that includes information about our MCP server
    system_prompt = SYSTEM_PROMPT
    
    # 初始化对话历史
    conversation_history = [
        {"role": "system", "content": system_prompt}
    ]
    
    # 开始聊天循环
    print("\n=== Blockchain Data Chat Mode ===")
    print("Type 'exit' to quit the chat")
    
    while True:
        # 获取用户输入
        user_message = input("\nYou: ")
        
        # 检查是否退出
        if user_message.lower() in ['exit', 'quit', 'bye']:
            print("Exiting chat mode...")
            break
        
        # 添加用户消息到历史记录
        conversation_history.append({"role": "user", "content": user_message})
        
        # Create a conversation with OpenAI
        print("Sending request to OpenAI...")
        try:
            # Add timeout to prevent hanging indefinitely
            response = client.chat.completions.create(
                model=model_name,  # 使用保存的模型名称而不是 args.model
                messages=conversation_history,
                tools=openai_tools,
                tool_choice="auto",
                timeout=30  # 30 seconds timeout
            )
            print("Received response from OpenAI")
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            continue
        
        # 获取助手响应
        assistant_message = response.choices[0].message
        
        # 添加助手响应到历史记录（包括可能的工具调用）
        assistant_response = {
            "role": "assistant",
            "content": assistant_message.content or ""
        }
        
        # 如果有工具调用，添加到助手消息中
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            assistant_response["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                } for tool_call in assistant_message.tool_calls
            ]
        
        # 将完整的助手响应添加到对话历史
        conversation_history.append(assistant_response)
        
        # 显示助手消息内容（如果有）
        if assistant_message.content:
            print(f"\nAssistant: {assistant_message.content}")
        
        # Check if OpenAI wants to call a function
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            tool_calls = assistant_message.tool_calls
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                print(f"\nOpenAI wants to call the {tool_name} function with these arguments:")
                args = json.loads(tool_call.function.arguments)
                print(json.dumps(args, indent=2))
                
                # Call the MCP server through the MCP protocol
                print(f"\nCalling MCP server tool: {tool_name}...")
                try:
                    result = await mcp_client.call_tool(tool_name, args)
                    print("Successfully called MCP tool")
                    
                    # Get the result as a string
                    print("Processing tool result...")
                    import pdb; pdb.set_trace()
                    # Convert result to string for OpenAI
                    try:
                        # Try to get a string representation that OpenAI can use
                        if hasattr(result, 'content') and hasattr(result.content, 'text'):
                            result_string = result.content.text
                        else:
                            result_string = str(result)
                        
                        # Add tool result to conversation history
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": result_string
                        })
                    except Exception as e:
                        print(f"Error processing result: {str(e)}")
                        # Use a simple error message as fallback
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": f"Error processing result: {str(e)}"
                        })
                    
                    # Send the result back to OpenAI for interpretation
                    print("\nSending follow-up request to OpenAI with the tool results...")
                    try:
                        follow_up_response = client.chat.completions.create(
                            model=model_name,  # 使用保存的模型名称而不是 args.model
                            messages=conversation_history,
                            timeout=30  # 30 seconds timeout
                        )
                        print("Received follow-up response from OpenAI")
                        
                        # 获取并显示解释结果
                        follow_up_message = follow_up_response.choices[0].message
                        print(f"\nAssistant: {follow_up_message.content}")
                        
                        # 添加解释结果到历史记录
                        conversation_history.append({"role": "assistant", "content": follow_up_message.content})
                        
                    except Exception as e:
                        print(f"Error calling OpenAI API for follow-up: {str(e)}")
                except Exception as e:
                    print(f"Error calling MCP tool: {str(e)}")
    
    # Close the MCP client connection
    await mcp_client.close()

async def main():
    try:
        # Test with OpenAI - this now handles starting and stopping the server internally
        await test_with_openai()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
