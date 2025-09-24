import sys
from pathlib import Path
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.stores import InMemoryStore
from langchain.agents import create_agent
from openai import AzureOpenAI

# Add the agent-service root directory to Python path
agent_service_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(agent_service_root))

from infra.exceptions.agent_exceptions import AgentException
from infra.logging import get_agent_logger
from src.app.services.database_provider import ProviderService
from src.app.database.transactions_db import db
from src.app.services.database_provider import ProviderService
from src.app.schemas.agent_prompt import system_prompt
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
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
        self.logger = get_agent_logger("TransactionAgent", "INFO")
        self.logger.info(f"Initializing TransactionAgent with model: {model_name}")

        self.model = AzureChatOpenAI(
            azure_deployment="gpt-4",
            api_version="2024-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            max_tokens=1000,
            temperature=0.5,
        )

        self.tools = self._create_tools()
        self.system_prompt = system_prompt
        self.provider_service = provider_service
        self.history_messages=[SystemMessage(content=self.system_prompt)]

        # Store for chat conversations
        self.store = InMemoryStore()

        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            store=self.store,
        )

        self.logger.info("TransactionAgent initialized successfully")

    def _create_tools(self):

        @tool("get_all_transactions_tool", return_direct=True, description="List all Transactions available in the database, use this when the user asks to see all transactions or wants a complete list, limited by 20 results;")
        async def get_all_transactions_tool(limit: int = 20, skip: int = 0):
            self.logger.info(f"Tool called: get_all_transactions_tool with limit={limit}, skip={skip}")
            try:
                transactions = await self.provider_service.get_all_transactions(limit=limit, skip=skip)

                if not transactions:
                    self.logger.info("No transactions found in database")
                    return "No transactions were found."

                result = f"Here are {len(transactions)} transactions (showing {skip+1}-{skip+len(transactions)}):\n\n"
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} | Customer: {transaction.get('customer_id')} | Amount: ${transaction.get('amount')} | Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                self.logger.info(f"Successfully retrieved {len(transactions)} transactions")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_all_transactions_tool: {str(e)}")
                raise AgentException() from e

        @tool("get_transaction_by_id_tool", return_direct=True, description="Get a specific transaction by its ID, use this when the user asks about a particular transaction")
        async def get_transaction_by_id_tool(transaction_id: str):
            self.logger.info(f"Tool called: get_transaction_by_id_tool with transaction_id={transaction_id}")
            try:
                transaction = await self.provider_service.get_transaction_by_id(transaction_id)

                if not transaction:
                    self.logger.warning(f"Transaction not found for ID: {transaction_id}")
                    return f"Transaction with ID '{transaction_id}' was not found."

                result = f"Transaction Details:\n"
                result += f"ID: {transaction.get('transaction_id')}\n"
                result += f"Customer ID: {transaction.get('customer_id')}\n"
                result += f"Amount: ${transaction.get('amount')}\n"
                result += f"Timestamp: {transaction.get('timestamp')}\n"
                result += f"Is Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                self.logger.info(f"Successfully retrieved transaction details for ID: {transaction_id}")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_transaction_by_id_tool: {str(e)}")
                raise AgentException() from e

        @tool("get_transactions_by_customer_tool", return_direct=True, description="Get all transactions for a specific customer ID, use this when the user asks about a customer's transaction history")
        async def get_transactions_by_customer_tool(customer_id: str):
            self.logger.info(f"Tool called: get_transactions_by_customer_tool with customer_id={customer_id}")
            try:
                transactions = await self.provider_service.get_transactions_by_customer(customer_id)

                if not transactions:
                    self.logger.warning(f"No transactions found for customer ID: {customer_id}")
                    return f"No transactions found for customer ID '{customer_id}'."

                result = f"Transaction history for customer {customer_id} ({len(transactions)} transactions):\n\n"
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} | Amount: ${transaction.get('amount')} | Date: {transaction.get('timestamp')} | Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                self.logger.info(f"Successfully retrieved {len(transactions)} transactions for customer: {customer_id}")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_transactions_by_customer_tool: {str(e)}")
                raise AgentException() from e

        @tool("get_fraud_transactions_tool", return_direct=True, description="Get all fraudulent transactions, use this when the user asks about fraud cases or suspicious transactions")
        async def get_fraud_transactions_tool():
            self.logger.info("Tool called: get_fraud_transactions_tool")
            try:
                transactions = await self.provider_service.get_fraud_transactions()

                if not transactions:
                    self.logger.info("No fraudulent transactions found in database")
                    return "No fraudulent transactions found."

                result = f"Fraudulent transactions found ({len(transactions)} total):\n\n"
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} | Customer: {transaction.get('customer_id')} | Amount: ${transaction.get('amount')} | Date: {transaction.get('timestamp')}\n"

                self.logger.info(f"Successfully retrieved {len(transactions)} fraudulent transactions")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_fraud_transactions_tool: {str(e)}")
                raise AgentException() from e

        @tool("get_transaction_stats_tool", return_direct=True, description="Get basic statistics about transactions including total count, fraud rate, and amounts, use this when the user asks for transaction statistics or summary")
        async def get_transaction_stats_tool():
            self.logger.info("Tool called: get_transaction_stats_tool")
            try:
                stats = await self.provider_service.get_transaction_stats()

                result = f"Transaction Statistics:\n\n"
                result += f"Total Transactions: {stats.get('total_transactions', 0):,}\n"
                result += f"Fraudulent Transactions: {stats.get('fraud_transactions', 0):,}\n"
                result += f"Fraud Rate: {stats.get('fraud_rate', 0):.2f}%\n"
                result += f"Average Transaction Amount: ${stats.get('average_amount', 0):.2f}\n"
                result += f"Total Transaction Amount: ${stats.get('total_amount', 0):,.2f}\n"

                self.logger.info(f"Successfully retrieved transaction statistics: total={stats.get('total_transactions', 0)}, fraud_rate={stats.get('fraud_rate', 0):.2f}%")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_transaction_stats_tool: {str(e)}")
                raise AgentException() from e

        return [get_all_transactions_tool, get_transaction_by_id_tool, get_transactions_by_customer_tool, get_fraud_transactions_tool, get_transaction_stats_tool]

    async def query(self, user_input: str, stream: bool = True):
        """
            Ensures the first message is the System Prompt initialized, then adds the user Input as HumanMessage
            It then invokes the agent by running once with the input and returning the final structured output;

            Args:
                user_input: User's query string
                stream: Whether to stream the response (default: True)
        """
        self.logger.info(f"Received user query: {user_input}")

        if not isinstance(self.history_messages[0], SystemMessage):
            self.history_messages.insert(0, SystemMessage(content=self.system_prompt))
            self.logger.debug("System prompt added to message history")

        # Add user input
        self.history_messages.append(HumanMessage(content=user_input))
        self.logger.debug("User input added to message history")

        # Prepare input for agent
        agent_input = {"messages": self.history_messages}

        try:
            if stream:
                self.logger.info("Streaming agent response with progress updates")
                return await self._stream_query(agent_input)
            else:
                self.logger.info("Invoking agent without streaming")
                result = await self.agent.ainvoke(agent_input)
                self.logger.info("Agent invocation completed successfully")
                return result
        except Exception as e:
            self.logger.error(f"Error during agent invocation: {str(e)}")
            raise AgentException() from e

    async def _stream_query(self, agent_input: dict):
        """
            Stream the agent's response with progress updates

            Args:
                agent_input: Input dictionary for the agent

            Yields:
                Progress updates and final result
        """
        self.logger.info("Starting streaming agent execution")
        final_result = None

        try:
            # Stream with "updates" mode to get agent progress
            async for chunk in self.agent.astream(agent_input, stream_mode="updates"):
                self.logger.debug(f"Streaming chunk received: {type(chunk)}")

                # Log tool execution progress
                if isinstance(chunk, dict):
                    if "tool_calls" in str(chunk):
                        self.logger.info("Tool execution in progress...")
                        print("Executing tool...")
                    elif "content" in str(chunk):
                        self.logger.info("Agent generating response...")
                        print("Agent thinking...")

                # Store the final result
                final_result = chunk

            self.logger.info("Streaming completed successfully")
            return final_result

        except Exception as e:
            self.logger.error(f"Error during streaming: {str(e)}")
            raise AgentException() from e


if __name__ == "__main__":
    async def main():
        provider_service = ProviderService(db)
        agent = TransactionAgent("gpt-4o", provider_service)
        agent.logger.info("Agent started in standalone mode")

        print("🚀 Transaction Agent is ready!")
        print("💡 Ask about transactions, fraud detection, or customer analysis")
        print("📋 Type 'help' for available commands, 'exit' or 'quit' to stop\n")

        while True:
            try:
                user_input = input("💬 Enter your query: ")

                if user_input.lower() in ['exit', 'quit']:
                    agent.logger.info("Agent shutting down")
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("\n📖 Available commands:")
                    print("• Ask about all transactions: 'show me all transactions'")
                    print("• Get transaction by ID: 'find transaction 12345'")
                    print("• Customer history: 'show transactions for customer ABC123'")
                    print("• Fraud analysis: 'show me fraudulent transactions'")
                    print("• Statistics: 'give me transaction statistics'")
                    print("• Non-streaming mode: 'no-stream [your query]'\n")
                    continue

                # Check if user wants non-streaming mode
                if user_input.lower().startswith('no-stream '):
                    query = user_input[10:]  # Remove 'no-stream ' prefix
                    print("⏳ Processing without streaming...")
                    response = await agent.query(query, stream=False)
                else:
                    print("⏳ Processing with streaming...")
                    response = await agent.query(user_input, stream=True)

                print(f"\n✅ Result:\n{response}\n")

            except KeyboardInterrupt:
                agent.logger.info("Agent interrupted by user")
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                agent.logger.error(f"Error in main loop: {str(e)}")
                print(f"❌ Error: {str(e)}\n")

    asyncio.run(main())