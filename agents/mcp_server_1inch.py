import os
import sys
import json
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 从环境变量获取 API 密钥
API_KEY = os.getenv("1INCH_API_KEY")
if not API_KEY:
    logger.error("1INCH_API_KEY 环境变量未设置")
    # 为测试目的，我们将继续使用虚拟密钥而不是抛出错误
    API_KEY = "dummy_key_for_testing"
    logger.warning("使用测试用的虚拟 API 密钥")

# 1inch API 基础 URL
BASE_URL = "https://api.1inch.dev/history/v2.0"
PORTFOLIO_BASE_URL = "https://api.1inch.dev/portfolio/portfolio/v4"

# 创建 MCP 服务器
mcp = FastMCP("1inch History API")

# 定义支持的链 ID
CHAIN_IDS = {
    "ethereum": "1",
    "optimism": "10", 
    "polygon": "137",
    "binance": "56",
    "arbitrum": "42161",
    "avalanche": "43114",
    "gnosis": "100",
    "fantom": "250",
    "aurora": "1313161554",
    "klaytn": "8217",
    "zksync": "324",
    "base": "8453",
    "linea": "59144",
    "mantle": "501"
}

#############################
# TOOLS
#############################

@mcp.tool()
def get_address_events(
    blockchain: str = "base", 
    address: str = None, 
    limit: int = 100, 
    token_address: str = None, 
    chain_id: int = None,  # Added as an alternative to blockchain
    from_timestamp_ms: int = None, 
    to_timestamp_ms: int = None, 
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get transaction events history for a specific address.
    
    Args:
        blockchain: Blockchain network (ethereum, optimism, polygon, binance, arbitrum, avalanche, gnosis, fantom, aurora, klaytn, zksync, base, linea, mantle)
        address: The address to query (required)
        limit: Number of events to return (default: 100, max: 2048)
        token_address: Filter events by token address
        chain_id: Direct chain ID value (alternative to blockchain parameter)
        from_timestamp_ms: Filter events from this timestamp (in milliseconds)
        to_timestamp_ms: Filter events to this timestamp (in milliseconds)
        offset: Pagination offset (default: 0)
        
    Returns:
        List of transaction events for the address
    """
    if not address:
        raise ValueError("address is required")
    
    # Determine chain ID - either use provided chain_id or look up from blockchain name
    if chain_id is None:
        # Validate and get chain ID from blockchain name
        chain_id = CHAIN_IDS.get(blockchain.lower())
        if not chain_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of: {', '.join(CHAIN_IDS.keys())}")
    
    # Limit the limit parameter
    if limit > 2048:
        limit = 2048  # API limit according to documentation
    
    # Build API URL
    url = f"{BASE_URL}/history/{address}/events"
    
    # Set request headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # Set query parameters
    params = {
        "chainId": chain_id,
        "limit": limit,
        "offset": offset
    }
    
    # Add optional parameters if provided
    if token_address:
        params["tokenAddress"] = token_address
    
    if from_timestamp_ms:
        params["fromTimestampMs"] = from_timestamp_ms
    
    if to_timestamp_ms:
        params["toTimestampMs"] = to_timestamp_ms
    
    try:
        # Send request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        # Return only the result field from the API response
        return result.get("result", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_portfolio_protocols_value_by_account(blockchain: str = "ethereum", addresses: List[str] = None, chain_id: int = None, use_cache: bool = True) -> Dict[str, Any]:
    """
    Get the current asset value in different protocols for specified wallet addresses.
    
    Args:
        blockchain: Blockchain network (ethereum, optimism, polygon, binance, arbitrum, avalanche, gnosis, fantom, aurora, klaytn, zksync, base, linea, mantle)
        addresses: List of wallet addresses to query (required)
        chain_id: Direct chain ID value (alternative to blockchain parameter)
        use_cache: Whether to get response from cache (default: True)
        
    Returns:
        Asset value information in different protocols
    """
    if not addresses:
        raise ValueError("addresses is required")
    
    # Determine chain ID - either use provided chain_id or look up from blockchain name
    if chain_id is None:
        # Validate and get chain ID from blockchain name
        chain_id = CHAIN_IDS.get(blockchain.lower())
        if not chain_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of: {', '.join(CHAIN_IDS.keys())}")
    
    # Build API URL
    url = f"{PORTFOLIO_BASE_URL}/overview/protocols/current_value"
    
    # Set request headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # Set request parameters
    params = {
        "addresses": addresses,
        "chain_id": chain_id,
        "use_cache": use_cache
    }
    
    try:
        # Send request
        response = requests.get(url, headers=headers, params=params)
        
        # Check for HTTP errors
        if response.status_code == 422:
            # Handle validation errors
            error_data = response.json()
            error_message = error_data.get("message", "Request parameter validation error")
            raise ValueError(f"API validation error: {error_message}")
        
        response.raise_for_status()
        result = response.json()
        
        # Return only the result field from the API response
        return result.get("result", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_portfolio_protocol_profit_and_loss_by_account(
    blockchain: str = "ethereum", 
    addresses: List[str] = None, 
    chain_id: int = None,
    timerange: str = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Get the profit and loss for specified wallet addresses in different protocols.
    
    Args:
        blockchain: Blockchain network (ethereum, optimism, polygon, binance, arbitrum, avalanche, gnosis, fantom, aurora, klaytn, zksync, base, linea, mantle)
        addresses: List of wallet addresses to query (required)
        chain_id: Direct chain ID value (alternative to blockchain parameter)
        timerange: Time range for profit and loss calculation (valid options: "1day", "1week", "1month", "1year", "3years")
        use_cache: Whether to get response from cache (default: True)
        
    Returns:
        Profit and loss information for the specified wallet addresses in different protocols
    """
    if not addresses:
        raise ValueError("addresses is required")
    
    # Validate timerange if provided
    valid_timeranges = ["1day", "1week", "1month", "1year", "3years"]
    if timerange and timerange not in valid_timeranges:
        raise ValueError(f"Invalid timerange: {timerange}. Must be one of: {', '.join(valid_timeranges)}")
    
    # Determine chain ID - either use provided chain_id or look up from blockchain name
    if chain_id is None:
        # Validate and get chain ID from blockchain name
        chain_id = CHAIN_IDS.get(blockchain.lower())
        if not chain_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of: {', '.join(CHAIN_IDS.keys())}")
    
    # Build API URL
    url = f"{PORTFOLIO_BASE_URL}/overview/protocols/profit_and_loss"
    
    # Set request headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # Set request parameters
    params = {
        "addresses": addresses,
        "chain_id": chain_id,
        "use_cache": use_cache
    }
    
    # Add optional timerange parameter if provided
    if timerange:
        params["timerange"] = timerange
    
    try:
        # Send request
        response = requests.get(url, headers=headers, params=params)
        
        # Check for HTTP errors
        if response.status_code == 422:
            # Handle validation errors
            error_data = response.json()
            error_message = error_data.get("message", "Request parameter validation error")
            raise ValueError(f"API validation error: {error_message}")
        
        response.raise_for_status()
        result = response.json()
        
        # Return only the result field from the API response
        return result.get("result", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_portfolio_token_profit_and_loss_by_account(
    blockchain: str = "ethereum", 
    addresses: List[str] = None, 
    chain_id: int = None,
    timerange: str = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Get the profit and loss for ERC20 tokens for specified wallet addresses.
    
    Args:
        blockchain: Blockchain network (ethereum, optimism, polygon, binance, arbitrum, avalanche, gnosis, fantom, aurora, klaytn, zksync, base, linea, mantle)
        addresses: List of wallet addresses to query (required)
        chain_id: Direct chain ID value (alternative to blockchain parameter)
        timerange: Time range for profit and loss calculation (valid options: "1day", "1week", "1month", "1year", "3years")
        use_cache: Whether to get response from cache (default: True)
        
    Returns:
        Profit and loss information for ERC20 tokens for the specified wallet addresses
    """
    if not addresses:
        raise ValueError("addresses is required")
    
    # Validate timerange if provided
    valid_timeranges = ["1day", "1week", "1month", "1year", "3years"]
    if timerange and timerange not in valid_timeranges:
        raise ValueError(f"Invalid timerange: {timerange}. Must be one of: {', '.join(valid_timeranges)}")
    
    # Determine chain ID - either use provided chain_id or look up from blockchain name
    if chain_id is None:
        # Validate and get chain ID from blockchain name
        chain_id = CHAIN_IDS.get(blockchain.lower())
        if not chain_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of: {', '.join(CHAIN_IDS.keys())}")
    
    # Build API URL
    url = f"{PORTFOLIO_BASE_URL}/overview/erc20/profit_and_loss"
    
    # Set request headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # Set request parameters
    params = {
        "addresses": addresses,
        "chain_id": chain_id,
        "use_cache": use_cache
    }
    
    # Add optional timerange parameter if provided
    if timerange:
        params["timerange"] = timerange
    
    try:
        # Send request
        response = requests.get(url, headers=headers, params=params)
        
        # Check for HTTP errors
        if response.status_code == 422:
            # Handle validation errors
            error_data = response.json()
            error_message = error_data.get("message", "Request parameter validation error")
            raise ValueError(f"API validation error: {error_message}")
        
        response.raise_for_status()
        result = response.json()
        
        # Return only the result field from the API response
        return result.get("result", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_general_current_value_by_address(
    blockchain: str = "ethereum", 
    addresses: List[str] = None, 
    chain_id: int = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Get the current value of assets for specified wallet addresses.
    
    Args:
        blockchain: Blockchain network (ethereum, optimism, polygon, binance, arbitrum, avalanche, gnosis, fantom, aurora, klaytn, zksync, base, linea, mantle)
        addresses: List of wallet addresses to query (required)
        chain_id: Direct chain ID value (alternative to blockchain parameter)
        use_cache: Whether to get response from cache (default: True)
        
    Returns:
        Current value information for the specified wallet addresses
    """
    if not addresses:
        raise ValueError("addresses is required")
    
    # Determine chain ID - either use provided chain_id or look up from blockchain name
    if chain_id is None:
        # Validate and get chain ID from blockchain name
        chain_id = CHAIN_IDS.get(blockchain.lower())
        if not chain_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of: {', '.join(CHAIN_IDS.keys())}")
    
    # Build API URL
    url = f"{PORTFOLIO_BASE_URL}/general/current_value"
    
    # Set request headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # Set request parameters
    params = {
        "addresses": addresses,
        "chain_id": chain_id,
        "use_cache": use_cache
    }
    
    try:
        # Send request
        response = requests.get(url, headers=headers, params=params)
        
        # Check for HTTP errors
        if response.status_code == 422:
            # Handle validation errors
            error_data = response.json()
            error_message = error_data.get("message", "Request parameter validation error")
            raise ValueError(f"API validation error: {error_message}")
        
        response.raise_for_status()
        result = response.json()
        
        # Return only the result field from the API response
        return result.get("result", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_general_profit_and_loss_by_address(
    blockchain: str = "ethereum", 
    addresses: List[str] = None, 
    chain_id: int = None,
    timerange: str = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Get the profit and loss information for specified wallet addresses.
    
    Args:
        blockchain: Blockchain network (ethereum, optimism, polygon, binance, arbitrum, avalanche, gnosis, fantom, aurora, klaytn, zksync, base, linea, mantle)
        addresses: List of wallet addresses to query (required)
        chain_id: Direct chain ID value (alternative to blockchain parameter)
        timerange: Time range for profit and loss calculation (valid options: "1day", "1week", "1month", "1year", "3years")
        use_cache: Whether to get response from cache (default: True)
        
    Returns:
        Profit and loss information for the specified wallet addresses
    """
    if not addresses:
        raise ValueError("addresses is required")
    
    # Validate timerange if provided
    valid_timeranges = ["1day", "1week", "1month", "1year", "3years"]
    if timerange and timerange not in valid_timeranges:
        raise ValueError(f"Invalid timerange: {timerange}. Must be one of: {', '.join(valid_timeranges)}")
    
    # Determine chain ID - either use provided chain_id or look up from blockchain name
    if chain_id is None:
        # Validate and get chain ID from blockchain name
        chain_id = CHAIN_IDS.get(blockchain.lower())
        if not chain_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of: {', '.join(CHAIN_IDS.keys())}")
    
    # Build API URL
    url = f"{PORTFOLIO_BASE_URL}/general/profit_and_loss"
    
    # Set request headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # Set request parameters
    params = {
        "addresses": addresses,
        "chain_id": chain_id,
        "use_cache": use_cache
    }
    
    # Add optional timerange parameter if provided
    if timerange:
        params["timerange"] = timerange
    
    try:
        # Send request
        response = requests.get(url, headers=headers, params=params)
        
        # Check for HTTP errors
        if response.status_code == 422:
            # Handle validation errors
            error_data = response.json()
            error_message = error_data.get("message", "Request parameter validation error")
            raise ValueError(f"API validation error: {error_message}")
        
        response.raise_for_status()
        result = response.json()
        
        # Return only the result field from the API response
        return result.get("result", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_general_value_chart_by_address(
    blockchain: str = "ethereum", 
    addresses: List[str] = None, 
    chain_id: int = None,
    timerange: str = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Get the value chart data for specified wallet addresses.
    
    Args:
        blockchain: Blockchain network (ethereum, optimism, polygon, binance, arbitrum, avalanche, gnosis, fantom, aurora, klaytn, zksync, base, linea, mantle)
        addresses: List of wallet addresses to query (required)
        chain_id: Direct chain ID value (alternative to blockchain parameter)
        timerange: Time range for value chart data (valid options: "1day", "1week", "1month", "1year", "3years")
        use_cache: Whether to get response from cache (default: True)
        
    Returns:
        Value chart data for the specified wallet addresses, including timestamps and values
    """
    if not addresses:
        raise ValueError("addresses is required")
    
    # Validate timerange if provided
    valid_timeranges = ["1day", "1week", "1month", "1year", "3years"]
    if timerange and timerange not in valid_timeranges:
        raise ValueError(f"Invalid timerange: {timerange}. Must be one of: {', '.join(valid_timeranges)}")
    
    # Determine chain ID - either use provided chain_id or look up from blockchain name
    if chain_id is None:
        # Validate and get chain ID from blockchain name
        chain_id = CHAIN_IDS.get(blockchain.lower())
        if not chain_id:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of: {', '.join(CHAIN_IDS.keys())}")
    
    # Build API URL
    url = f"{PORTFOLIO_BASE_URL}/general/value_chart"
    
    # Set request headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # Set request parameters
    params = {
        "addresses": addresses,
        "chain_id": chain_id,
        "use_cache": use_cache
    }
    
    # Add optional timerange parameter if provided
    if timerange:
        params["timerange"] = timerange
    
    try:
        # Send request
        response = requests.get(url, headers=headers, params=params)
        
        # Check for HTTP errors
        if response.status_code == 422:
            # Handle validation errors
            error_data = response.json()
            error_message = error_data.get("message", "Request parameter validation error")
            raise ValueError(f"API validation error: {error_message}")
        
        response.raise_for_status()
        result = response.json()
        
        # Return only the result field from the API response
        return result.get("result", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")

# Run the server
if __name__ == "__main__":
    # Record server startup
    logger.info("Starting 1inch MCP server, using stdio transport")
    logger.info(f"Python version: {sys.version}")
    logger.info("Server initialized and ready")
    
    try:
        # Use stdio transport, which is supported by FastMCP
        # This will allow the server to communicate via standard input/output
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Running MCP server failed: {str(e)}")
        raise