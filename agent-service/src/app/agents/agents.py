from langchain_core.tools import tool
from infra.exceptions.agent_exceptions import AgentException
from app.services.database_provider import ProviderService
from langchain_openai import ChatOpenAI
import os
class TransactionAgent():
    """
        This is an Agent, whose job is to use as many tools as possible to answer the user's query about Transactions;
    """

    def __init__(self, model_name : str, provider_service: ProviderService):
        """
            model = Initializes the Agent Model also known as the LLM
            tools = Gathers all the tools that the Agent can use
            system_prompt = This is the Agent's intstructions
            provider_service = It's a service layer that interacts with the database and the Agent Class
        """
        self.model = ChatOpenAI(
            model=model_name,
            temperature=0.5,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    
        self.tools = self._create_tools()
        self.system_prompt = "You're an AI Agent"
        self.provider_service = provider_service

    def _create_tools(self):

        @tool("get_all_transactions_tool", return_direct=True, description="List all Transactions available in the database, use this when the user asks to see all transactions or wants a complete list, limited by 20 results;")
        async def get_all_transactions_tool(limit: int = 20, skip: int = 0):
            try:
                transactions = await self.provider_service.get_all_transactions(limit=limit, skip=skip)

                if not transactions:
                    return "No transactions were found."

                result = f"Here are {len(transactions)} transactions (showing {skip+1}-{skip+len(transactions)}):\n\n"
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} | Customer: {transaction.get('customer_id')} | Amount: ${transaction.get('amount')} | Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                return result
            except Exception as e:
                raise AgentException() from e

        @tool("get_transaction_by_id_tool", return_direct=True, description="Get a specific transaction by its ID, use this when the user asks about a particular transaction")
        async def get_transaction_by_id_tool(transaction_id: str):
            try:
                transaction = await self.provider_service.get_transaction_by_id(transaction_id)

                if not transaction:
                    return f"Transaction with ID '{transaction_id}' was not found."

                result = f"Transaction Details:\n"
                result += f"ID: {transaction.get('transaction_id')}\n"
                result += f"Customer ID: {transaction.get('customer_id')}\n"
                result += f"Amount: ${transaction.get('amount')}\n"
                result += f"Timestamp: {transaction.get('timestamp')}\n"
                result += f"Is Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                return result
            except Exception as e:
                raise AgentException() from e

        @tool("get_transactions_by_customer_tool", return_direct=True, description="Get all transactions for a specific customer ID, use this when the user asks about a customer's transaction history")
        async def get_transactions_by_customer_tool(customer_id: str):
            try:
                transactions = await self.provider_service.get_transactions_by_customer(customer_id)

                if not transactions:
                    return f"No transactions found for customer ID '{customer_id}'."

                result = f"Transaction history for customer {customer_id} ({len(transactions)} transactions):\n\n"
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} | Amount: ${transaction.get('amount')} | Date: {transaction.get('timestamp')} | Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                return result
            except Exception as e:
                raise AgentException() from e

        @tool("get_fraud_transactions_tool", return_direct=True, description="Get all fraudulent transactions, use this when the user asks about fraud cases or suspicious transactions")
        async def get_fraud_transactions_tool():
            try:
                transactions = await self.provider_service.get_fraud_transactions()

                if not transactions:
                    return "No fraudulent transactions found."

                result = f"Fraudulent transactions found ({len(transactions)} total):\n\n"
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} | Customer: {transaction.get('customer_id')} | Amount: ${transaction.get('amount')} | Date: {transaction.get('timestamp')}\n"

                return result
            except Exception as e:
                raise AgentException() from e

        @tool("get_transaction_stats_tool", return_direct=True, description="Get basic statistics about transactions including total count, fraud rate, and amounts, use this when the user asks for transaction statistics or summary")
        async def get_transaction_stats_tool():
            try:
                stats = await self.provider_service.get_transaction_stats()

                result = f"Transaction Statistics:\n\n"
                result += f"Total Transactions: {stats.get('total_transactions', 0):,}\n"
                result += f"Fraudulent Transactions: {stats.get('fraud_transactions', 0):,}\n"
                result += f"Fraud Rate: {stats.get('fraud_rate', 0):.2f}%\n"
                result += f"Average Transaction Amount: ${stats.get('average_amount', 0):.2f}\n"
                result += f"Total Transaction Amount: ${stats.get('total_amount', 0):,.2f}\n"

                return result
            except Exception as e:
                raise AgentException() from e

        return [get_all_transactions_tool, get_transaction_by_id_tool, get_transactions_by_customer_tool, get_fraud_transactions_tool, get_transaction_stats_tool]
