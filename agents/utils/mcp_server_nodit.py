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
def get_tokens_owned_by_account(blockchain: str = "arbitrum", network: str = "mainnet", account_address: str = None, rpp: int = 20, cursor: str = None) -> List[Dict[str, Any]]:
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
        
        # Get the items array
        items = result.get("items", [])
        
        # Process each item to convert balance based on decimals
        for item in items:
            if "balance" in item and "contract" in item and "decimals" in item["contract"]:
                try:
                    # Convert the raw balance using the token's decimals
                    decimals = int(item["contract"]["decimals"])
                    raw_balance = item["balance"]
                    
                    # Only process if both values are valid
                    if decimals > 0 and raw_balance:
                        # Convert the raw balance to a human-readable format
                        converted_balance = float(raw_balance) / (10 ** decimals)
                        
                        # Add the converted balance as a new field
                        item["converted_balance"] = converted_balance
                        
                        # Replace the original balance with the converted balance
                        item["balance"] = converted_balance
                        
                    # Also convert totalSupply if present in the contract data
                    if "totalSupply" in item["contract"] and item["contract"]["totalSupply"]:
                        try:
                            raw_supply = item["contract"]["totalSupply"]
                            # Convert the raw supply to a human-readable format
                            converted_supply = float(raw_supply) / (10 ** decimals)
                            # Replace the original supply with the converted supply
                            item["contract"]["totalSupply"] = converted_supply
                        except (ValueError, TypeError):
                            # If conversion fails, keep the original supply
                            pass
                except (ValueError, TypeError):
                    # If conversion fails, keep the original balance
                    pass
        
        # Return just the items array
        return items
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
def get_token_transfers_by_account(blockchain: str = "arbitrum", network: str = "mainnet", account_address: str = None, rpp: int = 20, cursor: str = None, sort: str = "desc") -> List[Dict[str, Any]]:
    """
    Get the list of ERC20 token transfers for a specific account (sent or received).
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        account_address: The address of the account to check the token transfers for
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
        
        # Get the items array
        items = result.get("items", [])
        
        # Process each item to convert value based on decimals
        for item in items:
            if "value" in item and "contract" in item and "decimals" in item["contract"]:
                try:
                    # Convert the raw value using the token's decimals
                    decimals = int(item["contract"]["decimals"])
                    raw_value = item["value"]
                    
                    # Only process if both values are valid
                    if decimals > 0 and raw_value:
                        # Convert the raw value to a human-readable format
                        converted_value = float(raw_value) / (10 ** decimals)
                        
                        # Add the converted value as a new field
                        item["converted_value"] = converted_value
                        
                        # Replace the original value with the converted value
                        item["value"] = converted_value
                        
                    # Also convert totalSupply if present in the contract data
                    if "totalSupply" in item["contract"] and item["contract"]["totalSupply"]:
                        try:
                            raw_supply = item["contract"]["totalSupply"]
                            # Convert the raw supply to a human-readable format
                            converted_supply = float(raw_supply) / (10 ** decimals)
                            # Replace the original supply with the converted supply
                            item["contract"]["totalSupply"] = converted_supply
                        except (ValueError, TypeError):
                            # If conversion fails, keep the original supply
                            pass
                except (ValueError, TypeError):
                    # If conversion fails, keep the original value
                    pass
        
        # Return just the items array
        return items
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_token_transfers_by_contract(blockchain: str = "arbitrum", network: str = "mainnet", contract_address: str = None, rpp: int = 20, cursor: str = None, sort: str = "desc") -> List[Dict[str, Any]]:
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


@mcp.tool()
def create_webhook(
    blockchain: str = "ethereum", 
    network: str = "mainnet", 
    event_type: str = None, 
    description: str = None,
    webhook_url: str = None,
    condition: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a webhook to receive notifications for blockchain events.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        event_type: The type of event to subscribe to (ADDRESS_ACTIVITY, MINED_TRANSACTION, SUCCESSFUL_TRANSACTION, 
                   FAILED_TRANSACTION, TOKEN_TRANSFER, BELOW_THRESHOLD_BALANCE, BLOCK_PERIOD, 
                   BLOCK_LIST_CALLER, ALLOW_LIST_CALLER, LOG)
        description: A description for this webhook
        webhook_url: The URL that will receive webhook notifications
        condition: A dictionary containing conditions specific to the event type. Each event type requires
                  different condition parameters:
                  
                  For ADDRESS_ACTIVITY:
                  {"addresses": ["0x123...", "0x456..."]} - List of addresses to monitor
                  
                  For TOKEN_TRANSFER:
                  {"addresses": ["0x123..."]} - List of addresses to monitor, or
                  {"contractAddress": "0x123..."} - Contract address to monitor, or
                  {"contractAddress": "0x123...", "tokenId": "123"} - For NFTs, specify contract and token ID
                  
                  For BLOCK_PERIOD:
                  {"period": 1} - Receive notification every N blocks
                  
                  For BELOW_THRESHOLD_BALANCE:
                  {"address": "0x123...", "threshold": "1000000000000000000", "tokenAddress": "0x456..."}
                  
                  For MINED_TRANSACTION:
                  {"txHash": "0x123..."} - Transaction hash to monitor
                  
                  For SUCCESSFUL_TRANSACTION:
                  {"txHash": "0x123..."} - Transaction hash to monitor
                  
                  For FAILED_TRANSACTION:
                  {"txHash": "0x123..."} - Transaction hash to monitor
                  
                  For BLOCK_LIST_CALLER:
                  {"addresses": ["0x123..."]} - List of addresses to block
                  
                  For ALLOW_LIST_CALLER:
                  {"addresses": ["0x123..."]} - List of addresses to allow
                  
                  For LOG:
                  {"address": "0x123...", "topics": ["0x456..."]} - Contract address and event topics
        
    Returns:
        Webhook subscription details including the subscription ID
    """
    if not event_type:
        raise ValueError("event_type is required")
    
    if not webhook_url:
        raise ValueError("webhook_url is required")
    
    if not condition:
        raise ValueError("condition is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    url = f"{BASE_URL}/{blockchain}/{network}/webhooks"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    # Prepare the request payload
    payload = {
        "eventType": event_type,
        "notification": {
            "webhookUrl": webhook_url
        },
        "condition": condition
    }
    
    # Add description if provided
    if description:
        payload["description"] = description
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return the webhook details
        return result
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_webhook(
    blockchain: str = "ethereum", 
    network: str = "mainnet", 
    subscription_id: str = None
) -> Dict[str, Any]:
    """
    Get details of a specific webhook subscription.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        subscription_id: The ID of the webhook subscription to retrieve
        
    Returns:
        Webhook subscription details
    """
    if not subscription_id:
        raise ValueError("subscription_id is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    url = f"{BASE_URL}/{blockchain}/{network}/webhooks/{subscription_id}"
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return the webhook details
        return result
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def update_webhook(
    blockchain: str = "ethereum", 
    network: str = "mainnet", 
    subscription_id: str = None,
    description: str = None,
    webhook_url: str = None,
    condition: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Update an existing webhook subscription.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        subscription_id: The ID of the webhook subscription to update
        description: A new description for this webhook
        webhook_url: A new URL that will receive webhook notifications
        condition: New conditions specific to the event type
        
    Returns:
        Updated webhook subscription details
    """
    if not subscription_id:
        raise ValueError("subscription_id is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    url = f"{BASE_URL}/{blockchain}/{network}/webhooks/{subscription_id}"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    # Prepare the update payload
    payload = {}
    
    if description:
        payload["description"] = description
    
    if webhook_url:
        if "notification" not in payload:
            payload["notification"] = {}
        payload["notification"]["webhookUrl"] = webhook_url
    
    if condition:
        payload["condition"] = condition
    
    # If no updates were specified, raise an error
    if not payload:
        raise ValueError("At least one of description, webhook_url, or condition must be provided")
    
    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return the updated webhook details
        return result
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def delete_webhook(
    blockchain: str = "ethereum", 
    network: str = "mainnet", 
    subscription_id: str = None
) -> Dict[str, Any]:
    """
    Delete a webhook subscription.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        subscription_id: The ID of the webhook subscription to delete
        
    Returns:
        Confirmation of deletion
    """
    if not subscription_id:
        raise ValueError("subscription_id is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    url = f"{BASE_URL}/{blockchain}/{network}/webhooks/{subscription_id}"
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY
    }
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        
        # Return success message
        return {"status": "success", "message": f"Webhook subscription {subscription_id} deleted successfully"}
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


@mcp.tool()
def get_webhook_history(
    blockchain: str = "ethereum", 
    network: str = "mainnet", 
    subscription_id: str = None,
    rpp: int = 20,
    cursor: str = None
) -> List[Dict[str, Any]]:
    """
    Get the history of webhook notifications for a specific subscription.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        subscription_id: The ID of the webhook subscription
        rpp: The number of results per page (default: 20, max: 100)
        cursor: The cursor for pagination (default: None)
        
    Returns:
        List of webhook notification history items
    """
    if not subscription_id:
        raise ValueError("subscription_id is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    if rpp > 100:
        rpp = 100  # API limit
    
    url = f"{BASE_URL}/{blockchain}/{network}/webhooks/{subscription_id}/history"
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY
    }
    
    params = {
        "rpp": rpp
    }
    
    # Add cursor for pagination if provided
    if cursor:
        params["cursor"] = cursor
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return just the items array
        return result.get("items", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_daily_transaction_stats(
    blockchain: str = "ethereum", 
    network: str = "mainnet",
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Get daily transaction statistics for a specific blockchain.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        start_date: Start date for the query in YYYY-MM-DD format (max 100 days from start to end)
        end_date: End date for the query in YYYY-MM-DD format (max 100 days from start to end)
        
    Returns:
        Daily transaction count statistics
    """
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    # Default to current date if not provided
    if not start_date:
        # Get date from 30 days ago
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    if not end_date:
        # Get current date
        from datetime import datetime
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/{blockchain}/{network}/stats/getDailyTransactionsStats"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    # Prepare the request payload
    payload = {
        "startDate": start_date,
        "endDate": end_date
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return the items array directly
        return result.get("items", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_daily_active_accounts_stats_by_contract(
    blockchain: str = "ethereum", 
    network: str = "mainnet",
    contract_address: str = None,
    start_date: str = None,
    end_date: str = None
) -> List[Dict[str, Any]]:
    """
    Get daily active account statistics for a specific contract.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        contract_address: The address of the contract to get statistics for
        start_date: Start date for the query in YYYY-MM-DD format (max 100 days from start to end)
        end_date: End date for the query in YYYY-MM-DD format (max 100 days from start to end)
        
    Returns:
        Daily active account statistics for the specified contract
    """
    if not contract_address:
        raise ValueError("contract_address is required")
    
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    # Default to current date if not provided
    if not start_date:
        # Get date from 30 days ago
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    if not end_date:
        # Get current date
        from datetime import datetime
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/{blockchain}/{network}/stats/getDailyActiveAccountsStatsByContract"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    # Prepare the request payload
    payload = {
        "contractAddress": contract_address,
        "startDate": start_date,
        "endDate": end_date
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return the items array directly
        return result.get("items", [])
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_daily_active_accounts_stats(
    blockchain: str = "ethereum", 
    network: str = "mainnet",
    start_date: str = None,
    end_date: str = None
) -> List[Dict[str, Any]]:
    """
    Get daily active account statistics for a blockchain.
    
    Args:
        blockchain: The blockchain to query (ethereum, arbitrum, optimism, base, polygon, avalanche)
        network: The network to query (mainnet or sepolia)
        start_date: Start date for the query in YYYY-MM-DD format (max 100 days from start to end)
        end_date: End date for the query in YYYY-MM-DD format (max 100 days from start to end)
        
    Returns:
        Daily active account statistics for the blockchain
    """
    if blockchain not in BLOCKCHAINS:
        raise ValueError(f"Unsupported blockchain: {blockchain}. Must be one of {BLOCKCHAINS}")
    
    if network not in NETWORKS:
        raise ValueError(f"Unsupported network: {network}. Must be one of {NETWORKS}")
    
    # Default to current date if not provided
    if not start_date:
        # Get date from 30 days ago
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    if not end_date:
        # Get current date
        from datetime import datetime
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/{blockchain}/{network}/stats/getDailyActiveAccountsStats"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    # Prepare the request payload
    payload = {
        "startDate": start_date,
        "endDate": end_date
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Return the items array directly
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