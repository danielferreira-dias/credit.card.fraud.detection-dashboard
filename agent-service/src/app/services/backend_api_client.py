import httpx
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import asyncio
from infra.logging.logger import get_agent_logger

load_dotenv()

class BackendAPIClient:
    """
    HTTP client service for communicating with the backend API.
    Handles prediction requests and other backend operations.
    """

    def __init__(self):
        self.base_url = os.getenv("BACKEND_API_URL", "http://localhost:80")
        self.timeout = float(os.getenv("API_TIMEOUT", "30.0"))
        self.max_retries = int(os.getenv("API_MAX_RETRIES", "3"))
        self.logger = get_agent_logger("BackendAPIClient", "INFO")

        # HTTP client configuration
        self.client_config = {
            "timeout": httpx.Timeout(self.timeout),
            "follow_redirects": True,
            "limits": httpx.Limits(max_keepalive_connections=10, max_connections=20)
        }

        self.logger.info(f"BackendAPIClient initialized with base_url: {self.base_url}")

    async def predict_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Request fraud prediction for a specific transaction.

        Args:
            transaction_id: The ID of the transaction to predict

        Returns:
            Dict containing prediction results

        Raises:
            httpx.HTTPError: For HTTP-related errors
            ValueError: For invalid responses
        """
        endpoint = f"/transactions/{transaction_id}/predict"
        url = f"{self.base_url}{endpoint}"

        self.logger.info(f"Requesting prediction for transaction {transaction_id}")

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(**self.client_config) as client:
                    response = await client.get(url)
                    response.raise_for_status()

                    data = response.json()
                    self.logger.info(f"Prediction successful for transaction {transaction_id}: {data.get('prediction', 'unknown')}")
                    return data

            except httpx.TimeoutException as e:
                self.logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries} for transaction {transaction_id}")
                if attempt == self.max_retries - 1:
                    raise httpx.TimeoutException(f"Request timed out after {self.max_retries} attempts") from e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except httpx.HTTPStatusError as e:
                self.logger.error(f"HTTP {e.response.status_code} error for transaction {transaction_id}: {e.response.text}")
                if e.response.status_code == 404:
                    raise ValueError(f"Transaction {transaction_id} not found") from e
                elif e.response.status_code >= 500:
                    # Retry on server errors
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
                else:
                    # Don't retry on client errors (4xx)
                    raise

            except httpx.RequestError as e:
                self.logger.error(f"Request error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise httpx.RequestError(f"Request failed after {self.max_retries} attempts: {str(e)}") from e
                await asyncio.sleep(2 ** attempt)

    async def get_transaction_count(self) -> Dict[str, Any]:
        """
        Get the total count of transactions from the backend.

        Returns:
            Dict containing transaction count information
        """
        endpoint = "/transactions/transactions/count"
        url = f"{self.base_url}{endpoint}"

        self.logger.info("Requesting transaction count from backend")

        try:
            async with httpx.AsyncClient(**self.client_config) as client:
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Transaction count retrieved successfully: {data}")
                return data

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get transaction count: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the backend API is healthy and responsive.

        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Backend health check failed: {str(e)}")
            return False