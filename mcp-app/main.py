from mcp.server.fastmcp import FastMCP
import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Fraud Analysis Agent")

BASE_URL = "http://localhost:80"

"""
What I’d like to allow users to ask for the agent:
- Get a specific transaction;
- Get a list of transactions limited to maximum 20;
- Get the number of total transactions and fraudulent 
- Get the number of total transactions fraudulent or not from some filters like city, country, device payment, IP.
- Get a prediction of a transaction;
"""

async def _make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper function for making HTTP requests with error handling."""
    url = f"{BASE_URL}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except ValueError:
        return {"error": "Invalid JSON response"}

# Tools ------------------
@mcp.tool()
async def get_transaction_details(transaction_id: str) -> Dict[str, Any]:
    """
    Fetch complete transaction details including fraud prediction.

    Args:
        transaction_id: The unique identifier of the transaction

    Returns:
        Transaction details with fraud analysis or error message
    """
    return await _make_request(f"/transactions/{transaction_id}")

@mcp.tool()
async def analyze_fraud_prediction(transaction_id: str) -> Dict[str, Any]:
    """
    Get detailed fraud prediction analysis for a specific transaction.
    This provides the AI model's assessment and confidence score.

    Args:
        transaction_id: The unique identifier of the transaction

    Returns:
        Fraud prediction details with probability score and risk factors
    """
    return await _make_request(f"/transactions/{transaction_id}/predict")

@mcp.tool()
async def search_transactions(
    limit: Optional[int] = 20,
    skip: Optional[int] = 0,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    merchant: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search and filter transactions based on various criteria.
    Useful for finding patterns or investigating suspicious activity.

    Args:
        limit: Maximum number of transactions to return (default: 20, max: 100)
        skip: Number of transactions to skip for pagination (default: 0)
        min_amount: Minimum transaction amount filter
        max_amount: Maximum transaction amount filter
        merchant: Filter by merchant name (partial match)
        start_date: Filter transactions after this date (YYYY-MM-DD format)
        end_date: Filter transactions before this date (YYYY-MM-DD format)

    Returns:
        List of transactions matching the criteria
    """
    params = {"limit": min(limit or 20, 100), "skip": skip or 0}

    # Add optional filters
    if min_amount is not None:
        params["min_amount"] = min_amount
    if max_amount is not None:
        params["max_amount"] = max_amount
    if merchant:
        params["merchant"] = merchant
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    return await _make_request("/transactions/", params)

@mcp.tool()
async def get_fraud_statistics() -> Dict[str, Any]:
    """
    Get overall fraud detection statistics and transaction counts.
    Provides context for fraud analysis and system performance.

    Returns:
        Statistical overview of transactions and fraud detection metrics
    """
    return await _make_request("/transactions/transactions/count")


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')


