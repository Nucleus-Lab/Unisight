import os
import sys
import json
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("Zircuit API")

# Base URL for Zircuit API
BASE_URL = "https://api.mainnet.zircuit.com/v1"

# Valid period values for metrics
VALID_PERIODS = ["30", "90", "180", "365"]

# Valid months values for transaction count
VALID_MONTHS = ["1", "3", "6", "12"]

#############################
# TOOLS
#############################

@mcp.tool()
def get_daily_metrics(period: str = None) -> Dict[str, Any]:
    """
    Get daily metrics for the specified period.
    
    Args:
        period: The period in days to get metrics for (30, 90, 180, or 365)
        
    Returns:
        Daily metrics including transaction count, unique addresses, deployed contracts, gas used, and fees
    """
    if period not in VALID_PERIODS:
        raise ValueError(f"Invalid period: {period}. Must be one of {VALID_PERIODS}")
    
    url = f"{BASE_URL}/analytics/metrics/daily"
    
    headers = {
        "accept": "application/json"
    }
    
    params = {
        "period": period
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        # Return the result
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Error details: {error_detail}")
            except:
                logger.error(f"Status code: {e.response.status_code}, Response text: {e.response.text}")
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Failed to parse API response")
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_transaction_count(months: str = "1") -> Dict[str, Any]:
    """
    Get the total number of transactions grouped by day.
    
    Args:
        months: Number of months to get the data for (1, 3, 6, or 12)
        
    Returns:
        Transaction count data grouped by day
    """
    if months not in VALID_MONTHS:
        raise ValueError(f"Invalid months value: {months}. Must be one of {VALID_MONTHS}")
    
    url = f"{BASE_URL}/transactions/count"
    
    headers = {
        "accept": "application/json"
    }
    
    params = {
        "months": months
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        # Return the result
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Error details: {error_detail}")
            except:
                logger.error(f"Status code: {e.response.status_code}, Response text: {e.response.text}")
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Failed to parse API response")
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_erc20_token_top_holders(token_addr: str, limit: int = 100) -> Dict[str, Any]:
    """
    Get top holders of an ERC-20 token.
    
    Args:
        token_addr: The contract address of the ERC-20 token
        limit: The maximum number of top holders to return
        
    Returns:
        Top holders of the specified ERC-20 token
    """
    if not token_addr:
        raise ValueError("token_addr is required")
    
    url = f"{BASE_URL}/erc20tokens/{token_addr}/top-holders"
    
    headers = {
        "accept": "application/json"
    }
    
    params = {}
    if limit:
        params["limit"] = limit
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        # Return the result
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Error details: {error_detail}")
            except:
                logger.error(f"Status code: {e.response.status_code}, Response text: {e.response.text}")
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Failed to parse API response")
        raise Exception("Failed to parse API response")


@mcp.tool()
def get_internal_transactions_by_address(address: str, limit: int = 10, next: str = None, previous: str = None) -> Dict[str, Any]:
    """
    Get a list of internal transactions by address.
    
    Args:
        address: The address to get internal transactions for
        limit: The maximum number of transactions to return
        next: Cursor value required to get the next page of results
        previous: Cursor value required to get the previous page of results
        
    Returns:
        List of internal transactions for the specified address with pagination information
    """
    if not address:
        raise ValueError("address is required")
    
    url = f"{BASE_URL}/address/{address}/internal"
    
    headers = {
        "accept": "application/json"
    }
    
    params = {}
    if limit:
        params["limit"] = limit
    if next:
        params["next"] = next
    if previous:
        params["previous"] = previous
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        # Return the result
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Error details: {error_detail}")
            except:
                logger.error(f"Status code: {e.response.status_code}, Response text: {e.response.text}")
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Failed to parse API response")
        raise Exception("Failed to parse API response")


# Run the server
if __name__ == "__main__":
    # Record server startup
    logger.info("Starting Zircuit API MCP server, using stdio transport")
    logger.info(f"Python version: {sys.version}")
    logger.info("Server initialized and ready")
    
    try:
        # Use stdio transport, which is supported by FastMCP
        # This will allow the server to communicate via standard input/output
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Running MCP server failed: {str(e)}")