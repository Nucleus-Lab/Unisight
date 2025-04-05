import os
import sys
import json
import requests
import logging
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
def get_tokens_owned_by_account(blockchain: str = "arbitrum", network: str = "mainnet", account_address: str = None, rpp: int = 20, cursor: str = None) -> Dict[str, Any]:
    """
    Get the list of ERC20 tokens owned by a specific account address.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        account_address: The address of the account to check the token holdings for
        rpp: The number of results per page (default: 20, max: 100)
        cursor: The cursor for pagination (default: None)
        
    Returns:
        List of token ownership details
    """
    if not account_address:
        raise ValueError("account_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if rpp > 100:
        rpp = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokensOwnedByAccount"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "accountAddress": account_address,
        "rpp": rpp
    }
    
    # Add cursor for pagination if provided
    if cursor:
        data["cursor"] = cursor
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return just the items array
        return result.get("items", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_holders_by_contract(blockchain: str = "arbitrum", network: str = "mainnet", contract_address: str = None, rpp: int = 20, cursor: str = None) -> Dict[str, Any]:
    """
    Get the list of token holders for a specific ERC20 token contract.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        contract_address: The contract address of the ERC20 token
        rpp: The number of results per page (default: 20, max: 100)
        cursor: The cursor for pagination (default: None)
        
    Returns:
        Dictionary containing rpp, cursor, and items with token holder details
    """
    if not contract_address:
        raise ValueError("contract_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if rpp > 100:
        rpp = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokenHoldersByContract"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "contractAddress": contract_address,
        "rpp": rpp
    }
    
    # Add cursor for pagination if provided
    if cursor:
        data["cursor"] = cursor
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return the response in the expected format
        return {
            "rpp": result.get("rpp", rpp),
            "cursor": result.get("cursor", None),
            "items": result.get("items", [])
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_transfers_by_account(blockchain: str = "arbitrum", network: str = "mainnet", account_address: str = None, rpp: int = 20, cursor: str = None, sort: str = "desc") -> Dict[str, Any]:
    """
    Get the list of ERC20 token transfers for a specific account (sent or received).
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        account_address: The address of the account to get transfers for
        rpp: The number of results per page (default: 20, max: 100)
        cursor: The cursor for pagination (default: None)
        sort: The sort order for transfers (asc or desc by timestamp, default: desc)
        
    Returns:
        List of token transfer details
    """
    if not account_address:
        raise ValueError("account_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if rpp > 100:
        rpp = 100  # API limit
    
    if sort not in ["asc", "desc"]:
        sort = "desc"  # Default to descending order
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokenTransfersByAccount"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "accountAddress": account_address,
        "rpp": rpp,
        "sort": sort
    }
    
    # Add cursor for pagination if provided
    if cursor:
        data["cursor"] = cursor
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return just the items array
        return result.get("items", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_transfers_by_contract(blockchain: str = "arbitrum", network: str = "mainnet", contract_address: str = None, rpp: int = 20, cursor: str = None, sort: str = "desc") -> Dict[str, Any]:
    """
    Get the list of ERC20 token transfers for a specific token contract.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        contract_address: The contract address of the ERC20 token
        rpp: The number of results per page (default: 20, max: 100)
        cursor: The cursor for pagination (default: None)
        sort: The sort order for transfers (asc or desc by timestamp, default: desc)
        
    Returns:
        List of token transfer details
    """
    if not contract_address:
        raise ValueError("contract_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if rpp > 100:
        rpp = 100  # API limit
    
    if sort not in ["asc", "desc"]:
        sort = "desc"  # Default to descending order
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/getTokenTransfersByContract"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "contractAddress": contract_address,
        "rpp": rpp,
        "sort": sort
    }
    
    # Add cursor for pagination if provided
    if cursor:
        data["cursor"] = cursor
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return just the items array
        return result.get("items", [])
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
        List of token price information including currency, price, market data and contract details
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
    
    # Normalize contract addresses to lowercase
    normalized_addresses = [addr.lower() for addr in contract_addresses]
    
    data = {
        "contractAddresses": normalized_addresses
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()  # API returns an array directly
        
        # Return the API response directly without transformation
        return result
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def search_token_contract_by_keyword(blockchain: str = "arbitrum", network: str = "mainnet", keyword: str = None, rpp: int = 20, cursor: str = None) -> Dict[str, Any]:
    """
    Search for ERC20 token contracts by matching the keyword with token name or symbol.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        keyword: The keyword to search for in token names or symbols
        rpp: The number of results per page (default: 20, max: 100)
        cursor: The cursor for pagination (default: None)
        
    Returns:
        List of token contract details
    """
    if not keyword:
        raise ValueError("keyword is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if rpp > 100:
        rpp = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/token/searchTokenContractMetadataByKeyword"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    data = {
        "keyword": keyword,
        "rpp": rpp
    }
    
    # Add cursor for pagination if provided
    if cursor:
        data["cursor"] = cursor
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return just the items array
        return result.get("items", [])
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
