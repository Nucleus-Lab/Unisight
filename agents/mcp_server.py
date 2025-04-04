import os
import sys
import json
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
# from mcp.server.prompt import PromptTemplate
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("NODIT_API_KEY")
if not API_KEY:
    logger.error("NODIT_API_KEY environment variable is not set")
    # For testing purposes, we'll continue with a dummy key instead of raising an error
    API_KEY = "dummy_key_for_testing"
    logger.warning("Using dummy API key for testing purposes")

# Base URL for Nodit.io API
BASE_URL = "https://web3.nodit.io/v1"

# Create an MCP server
mcp = FastMCP("Nodit.io Web3 API")

# Define supported networks
NETWORKS = ["mainnet", "sepolia"]

# Define supported blockchains
BLOCKCHAINS = ["ethereum", "arbitrum", "optimism", "base", "polygon", "avalanche"]

#############################
# TOOLS
#############################


@mcp.tool()
def get_tokens_owned_by_account(blockchain: str = "arbitrum", network: str = "mainnet", account_address: str = None, page: int = 1, limit: int = 10, with_count: bool = False) -> Dict[str, Any]:
    """
    Get the list of ERC20 tokens owned by a specific account address.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        account_address: The address of the account to check the token holdings for
        page: The page number for pagination (default: 1)
        limit: The number of tokens to return per page (default: 10, max: 100)
        with_count: Whether to include token count in the response (default: False)
        
    Returns:
        List of tokens owned by the account with their balances and metadata
    """
    if not account_address:
        raise ValueError("account_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if limit > 100:
        limit = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokensOwnedByAccount"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "accountAddress": account_address,
        "withCount": with_count
    }
    
    # 只有在需要分页时才添加这些参数
    if page > 1 or limit != 10:
        data["page"] = page
        data["limit"] = limit
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Process the tokens - 根据实际 API 响应格式调整
        tokens = []
        # API 返回的是 "items" 数组而不是 "tokens" 数组
        for token in result.get("items", []):
            contract = token.get("contract", {})
            tokens.append({
                "contractAddress": contract.get("address", ""),
                "name": contract.get("name", ""),
                "symbol": contract.get("symbol", ""),
                "decimals": contract.get("decimals", 0),
                "balance": token.get("balance", "0")
            })
        
        return {
            "tokens": tokens,
            "page": page,
            "limit": limit,
            "total": len(tokens)  # 使用实际返回的令牌数量
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_holders_by_contract(blockchain: str = "arbitrum", network: str = "mainnet", contract_address: str = None, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """
    Get the list of token holders for a specific ERC20 token contract.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        contract_address: The contract address of the ERC20 token
        page: The page number for pagination (default: 1)
        limit: The number of holders to return per page (default: 10, max: 100)
        
    Returns:
        Token information and a list of holders with their balances and percentages
    """
    if not contract_address:
        raise ValueError("contract_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if limit > 100:
        limit = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokenHoldersByContract"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "contractAddress": contract_address
    }
    
    # 只有在需要分页时才添加这些参数
    if page > 1 or limit != 10:
        data["page"] = page
        data["limit"] = limit
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # 获取代币信息
        contract_info = result.get("contract", {})
        token_info = {
            "name": contract_info.get("name", ""),
            "symbol": contract_info.get("symbol", ""),
            "decimals": contract_info.get("decimals", 0),
            "totalSupply": contract_info.get("totalSupply", "0"),
            "contractAddress": contract_address
        }
        
        # 处理持有者信息
        holders = []
        for holder in result.get("items", []):
            holders.append({
                "address": holder.get("holderAddress", ""),
                "balance": holder.get("balance", "0"),
                "percentage": holder.get("percentage", 0.0)
            })
        
        return {
            "token": token_info,
            "holders": holders,
            "page": page,
            "limit": limit,
            "total": len(holders)
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_transfers_by_account(blockchain: str = "arbitrum", network: str = "mainnet", account_address: str = None, page: int = 1, limit: int = 10, sort: str = "desc") -> Dict[str, Any]:
    """
    Get the list of ERC20 token transfers for a specific account (sent or received).
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        account_address: The address of the account to get transfers for
        page: The page number for pagination (default: 1)
        limit: The number of transfers to return per page (default: 10, max: 100)
        sort: The sort order for transfers (asc or desc by timestamp, default: desc)
        
    Returns:
        List of token transfers with token information, transaction details, and amounts
    """
    if not account_address:
        raise ValueError("account_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if sort not in ["asc", "desc"]:
        raise ValueError("sort must be either 'asc' or 'desc'")
    
    if limit > 100:
        limit = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokenTransfersByAccount"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "accountAddress": account_address
    }
    
    # 只有在需要分页或排序时才添加这些参数
    if page > 1 or limit != 10 or sort != "desc":
        data["page"] = page
        data["limit"] = limit
        data["sort"] = sort
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # 处理转账记录
        transfers = []
        for transfer in result.get("items", []):
            # 获取代币合约信息
            contract = transfer.get("contract", {})
            
            # 构建转账记录
            transfer_data = {
                "transactionHash": transfer.get("transactionHash", ""),
                "blockNumber": transfer.get("blockNumber", 0),
                "timestamp": transfer.get("timestamp", 0),
                "from": transfer.get("from", ""),
                "to": transfer.get("to", ""),
                "value": transfer.get("value", "0"),
                "token": {
                    "contractAddress": contract.get("address", ""),
                    "name": contract.get("name", ""),
                    "symbol": contract.get("symbol", ""),
                    "decimals": contract.get("decimals", 0)
                }
            }
            transfers.append(transfer_data)
        
        return {
            "transfers": transfers,
            "page": page,
            "limit": limit,
            "total": len(transfers)
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_transfers_by_contract(blockchain: str = "arbitrum", network: str = "mainnet", contract_address: str = None, page: int = 1, limit: int = 10, sort: str = "desc") -> Dict[str, Any]:
    """
    Get the list of ERC20 token transfers for a specific token contract.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        contract_address: The contract address of the ERC20 token
        page: The page number for pagination (default: 1)
        limit: The number of transfers to return per page (default: 10, max: 100)
        sort: The sort order for transfers (asc or desc by timestamp, default: desc)
        
    Returns:
        List of token transfers with transaction details and amounts
    """
    if not contract_address:
        raise ValueError("contract_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if sort not in ["asc", "desc"]:
        raise ValueError("sort must be either 'asc' or 'desc'")
    
    if limit > 100:
        limit = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokenTransfersByContract"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "contractAddress": contract_address
    }
    
    # 只有在需要分页或排序时才添加这些参数
    if page > 1 or limit != 10 or sort != "desc":
        data["page"] = page
        data["limit"] = limit
        data["sort"] = sort
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # 获取代币合约信息 - 从第一个转账记录中获取合约信息
        contract_info = {}
        if result.get("items") and len(result.get("items", [])) > 0:
            contract_info = result.get("items", [])[0].get("contract", {})
        
        token_info = {
            "contractAddress": contract_info.get("address", ""),
            "name": contract_info.get("name", ""),
            "symbol": contract_info.get("symbol", ""),
            "decimals": contract_info.get("decimals", 0),
            "totalSupply": contract_info.get("totalSupply", "0"),
            "deployedAt": contract_info.get("deployedAt"),
            "deployerAddress": contract_info.get("deployerAddress"),
            "type": contract_info.get("type")
        }
        
        # 处理转账记录
        transfers = []
        for transfer in result.get("items", []):
            transfer_data = {
                "transactionHash": transfer.get("transactionHash", ""),
                "blockNumber": transfer.get("blockNumber", 0),
                "timestamp": transfer.get("timestamp", 0),
                "from": transfer.get("from", ""),
                "to": transfer.get("to", ""),
                "value": transfer.get("value", "0"),
                "logIndex": transfer.get("logIndex")
            }
            transfers.append(transfer_data)
        
        return {
            "token": token_info,
            "transfers": transfers,
            "page": page,
            "limit": limit,
            "total": len(transfers),
            "rpp": result.get("rpp"),
            "cursor": result.get("cursor")
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_prices_by_contracts(blockchain: str = "arbitrum", network: str = "mainnet", contract_addresses: List[str] = None) -> Dict[str, Any]:
    """
    Get the prices of multiple ERC20 tokens by their contract addresses.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        contract_addresses: List of contract addresses to get prices for (max 100)
        
    Returns:
        List of token price information including USD value and market data
    """
    if not contract_addresses:
        raise ValueError("contract_addresses is required and must be a non-empty list")
    
    if len(contract_addresses) > 100:
        raise ValueError("Maximum of 100 contract addresses can be queried at once")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokenPricesByContracts"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    # 确保合约地址是小写的
    normalized_addresses = [addr.lower() for addr in contract_addresses]
    
    data = {
        "contractAddresses": normalized_addresses  # 使用 contractAddresses 而不是 contracts
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()  # 直接返回数组，不是包含 items 的对象
        
        # 处理价格数据
        token_prices = []
        for price_data in result:  # 直接遍历结果数组
            # 获取代币合约信息
            contract = price_data.get("contract", {})
            
            # 构建价格信息
            price_info = {
                "contractAddress": contract.get("address", ""),
                "name": contract.get("name", ""),
                "symbol": contract.get("symbol", ""),
                "decimals": contract.get("decimals", 0),
                "totalSupply": contract.get("totalSupply", "0"),
                "currency": price_data.get("currency", "USD"),
                "price": price_data.get("price"),
                "volumeFor24h": price_data.get("volumeFor24h"),
                "volumeChangeFor24h": price_data.get("volumeChangeFor24h"),
                "percentChangeFor1h": price_data.get("percentChangeFor1h"),
                "percentChangeFor24h": price_data.get("percentChangeFor24h"),
                "percentChangeFor7d": price_data.get("percentChangeFor7d"),
                "marketCap": price_data.get("marketCap"),
                "updatedAt": price_data.get("updatedAt"),
                "listings": price_data.get("listings", [])
            }
            token_prices.append(price_info)
        
        return {
            "prices": token_prices,
            "count": len(token_prices)
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def search_token_contract_by_keyword(blockchain: str = "arbitrum", network: str = "mainnet", keyword: str = None, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """
    Search for ERC20 token contracts by matching the keyword with token name or symbol.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        keyword: The keyword to search for in token names or symbols
        page: The page number for pagination (default: 1)
        limit: The number of results to return per page (default: 10, max: 100)
        
    Returns:
        List of token contracts matching the search keyword
    """
    if not keyword:
        raise ValueError("keyword is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if limit > 100:
        limit = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/searchTokenContractMetadataByKeyword"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "keyword": keyword
    }
    
    # 只有在需要分页时才添加这些参数
    if page > 1 or limit != 10:
        data["page"] = page
        data["limit"] = limit
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # 处理搜索结果
        tokens = []
        for token in result.get("items", []):
            token_info = {
                "address": token.get("address", ""),
                "name": token.get("name", ""),
                "symbol": token.get("symbol", ""),
                "decimals": token.get("decimals", 0),
                "totalSupply": token.get("totalSupply", "0"),
                "deployedAt": token.get("deployedAt"),
                "deployerAddress": token.get("deployerAddress"),
                "type": token.get("type", "ERC20"),
                "logoUrl": token.get("logoUrl")
            }
            tokens.append(token_info)
        
        return {
            "tokens": tokens,
            "page": page,
            "limit": limit,
            "total": len(tokens),
            "rpp": result.get("rpp"),
            "cursor": result.get("cursor")
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


# Run the server
if __name__ == "__main__":
    # Log server startup
    logger.info("Starting MCP server with stdio transport")
    logger.info(f"Python version: {sys.version}")
    # FastMCP doesn't have a tools attribute directly accessible
    logger.info("Server initialized and ready")
    
    try:
        # Use stdio transport which is supported by FastMCP
        # This will allow the server to communicate via standard input/output
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}")
        raise
