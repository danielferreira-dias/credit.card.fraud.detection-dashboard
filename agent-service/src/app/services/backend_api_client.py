import httpx
import os
from typing import Dict, Any
from dotenv import load_dotenv
from infra.logging.logger import get_agent_logger
from infra.exceptions.agent_exceptions import BackendClientException
from fastapi import Depends
from app.schemas.query_schema import TransactionFilter


load_dotenv()

class BackendAPIClient:
    """
    HTTP client service for communicating with the backend API.
    Handles prediction requests and other backend operations.
    """

    def __init__(self):
        self.base_url = os.getenv("BACKEND_API_URL", "http://localhost:80")
        self.logger = get_agent_logger("BackendAPIClient", "INFO")
        self.logger.info(f"BackendAPIClient initialized with base_url: {self.base_url}")
    
    async def get_transaction_count(self) -> Dict[str, Any]:
        """
        Get the total count of transactions from the backend.

        Returns:
            Dict containing transaction count information
        """
        endpoint = "/transactions/count"
        url = f"{self.base_url}{endpoint}"
        self.logger.info("Requesting transaction count from backend")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Transaction count retrieved successfully: {data}")
                return data

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get transaction count: {str(e)}")
            raise BackendClientException(f"Failed to get transaction count: {str(e)}")
        
    async def get_transaction_count_filtered(self, filters: TransactionFilter) -> Dict[str, Any]:
        """
        Get the count of transactions matching the given filters from the backend.

        Args:
            filters: Optional filters to apply
        Returns:
            Dict containing filtered transaction count information
        """
        endpoint = "/transactions/filtered/count"
        url = f"{self.base_url}{endpoint}"

        params = {}
        if filters:
            params.update(filters)

        self.logger.info(f"Requesting filtered transaction count with filters: {filters}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Filtered transaction count retrieved successfully: {data}")
                return data

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get filtered transaction count: {str(e)}")
            raise BackendClientException(f"Failed to get filtered transaction count: {str(e)}")

    async def get_transactions(self, limit: int = 20, skip: int = 0) -> Dict[str, Any]:
        """
        Get a list of transactions with pagination.

        Args:
            limit: Maximum number of transactions to return (default 20)
            skip: Number of transactions to skip (default 0)

        Returns:
            List of transactions
        """
        endpoint = "/transactions/"
        url = f"{self.base_url}{endpoint}"

        params = {"limit": limit, "skip": skip}

        self.logger.info(f"Requesting transactions list with limit={limit}, skip={skip}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Transactions list retrieved successfully: {len(data) if isinstance(data, list) else 'unknown'} transactions")
                return data

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get transactions list: {str(e)}")
            raise BackendClientException(f"Failed to get transactions list: {str(e)}")
        
    async def get_transactions_filtered(self, filters: TransactionFilter = Depends(), limit: int = 20, skip: int = 0) -> Dict[str, Any]:
        """
        Get a list of transactions with optional filtering and pagination.

        Args:
            filters: Optional filters to apply
            limit: Maximum number of transactions to return (default 20)
            skip: Number of transactions to skip (default 0)

        Returns:
            List of transactions matching the criteria
        """
        endpoint = "/transactions/"
        url = f"{self.base_url}{endpoint}"

        params = {"limit": limit, "skip": skip}
        if filters:
            params.update(filters)

        self.logger.info(f"Requesting transactions list with filters: {filters}, limit: {limit}, skip: {skip}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Transactions list retrieved successfully: {len(data) if isinstance(data, list) else 'unknown'} transactions")
                return data

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get transactions list: {str(e)}")
            raise BackendClientException(f"Failed to get transactions list: {str(e)}")

    async def get_transactions_stats(self) -> Dict[str, Any]:
        """
        Get statistics about transactions from the backend.

        Returns:
            Dict containing transaction statistics
        """
        endpoint = "/transactions/stats"
        url = f"{self.base_url}{endpoint}"
        self.logger.info("Requesting transaction statistics from backend")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Transaction statistics retrieved successfully: {data}")
                return data

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get transaction statistics: {str(e)}")
            raise BackendClientException(f"Failed to get transaction statistics: {str(e)}")
    
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
        try:
            async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    response.raise_for_status()

                    data = response.json()
                    self.logger.info(f"Prediction successful for transaction {transaction_id}: {data.get('prediction', 'unknown')}")
                    return data
        except Exception as e:
            self.logger.error(f"Unexpected error during prediction request: {str(e)}")
            raise BackendClientException(f"Unexpected error during prediction request: {str(e)}")

    async def get_transaction_by_id(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get a specific transaction by its ID.

        Args:
            transaction_id: The ID of the transaction to retrieve

        Returns:
            Dict containing transaction details
        """
        endpoint = f"/transactions/{transaction_id}"
        url = f"{self.base_url}{endpoint}"

        self.logger.info(f"Requesting transaction details for ID: {transaction_id}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Transaction details retrieved successfully for ID: {transaction_id}")
                return data

        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get transaction {transaction_id}: {str(e)}")
            raise BackendClientException(f"Failed to get transaction {transaction_id}: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if the backend API is healthy and responsive.

        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/")
                return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Backend health check failed: {str(e)}")
            return False