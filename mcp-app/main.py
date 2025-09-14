from mcp.server.fastmcp import FastMCP
import httpx

# Create an MCP server
mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
async def get_transaction_info(transaction_id: str) -> dict:
    """
    Fetch transaction details by its ID.
    """
    url = f"http://localhost:80/transactions/{transaction_id}"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except ValueError:
        return {"error": "Invalid JSON response"}


