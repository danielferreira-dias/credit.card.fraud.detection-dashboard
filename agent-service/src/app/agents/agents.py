import sys
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, Annotated
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.stores import InMemoryStore
from langsmith import traceable

# Add the agent-service root directory to Python path
agent_service_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(agent_service_root))

from infra.exceptions.agent_exceptions import AgentException
from infra.logging import get_agent_logger
from app.services.database_provider import ProviderService
from app.services.backend_api_client import BackendAPIClient
from app.schemas.agent_prompt import system_prompt
from langgraph.prebuilt import create_react_agent

import os
from dotenv import load_dotenv

load_dotenv()
class TransactionAgent():
    """
        This is an Agent, whose job is to use as many tools as possible to answer the user's query about Transactions;
    """

    def __init__(self, model_name : str, provider_service: ProviderService, backend_client: BackendAPIClient):
        """
            model = Initializes the Agent Model also known as the LLM
            tools = Gathers all the tools that the Agent can use
            system_prompt = This is the Agent's intstructions
            provider_service = It's a service layer that interacts with the database and the Agent Class
        """
        self.logger = get_agent_logger("TransactionAgent", "INFO")
        self.logger.info(f"Initializing TransactionAgent with model: {model_name}")

        self.model = AzureChatOpenAI(
            azure_deployment=model_name,
            api_version="2024-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            max_tokens=1000,
            temperature=0.5,
        )

        # Enable LangSmith tracing if configured

        self.tools = self._create_tools()
        self.system_prompt = system_prompt
        self.provider_service = provider_service
        self.backend_client = backend_client
        self.history_messages=[SystemMessage(content=self.system_prompt)]

        # Store for chat conversations
        self.store = InMemoryStore()

        # Initialize both ReAct agent and LangGraph workflow
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            store=self.store,
        )
        # self.agent = create_agent(
        #     model=self.model,
        #     tools=self.llm_with_tools,
        #     store=self.store,
        # )

        self.logger.info("TransactionAgent initialized successfully")

    def _create_tools(self):

        @tool("get_all_transactions_tool", description="List all Transactions available in the database, use this when the user asks to see all transactions or wants a complete list, limited by 20 results;")
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

        @tool("get_transaction_by_id_tool", description="Get a specific transaction by its ID, use this when the user asks about a particular transaction")
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

        @tool("get_transactions_by_customer_tool", description="Get all transactions for a specific customer ID, use this when the user asks about a customer's transaction history")
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

        @tool("get_fraud_transactions_tool", description="Get all fraudulent transactions, use this when the user asks about fraud cases or suspicious transactions")
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

        @tool("get_transaction_stats_tool", description="Get basic statistics about transactions including total count, fraud rate, and amounts, use this when the user asks for transaction statistics or summary")
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

        @tool("search_transactions_by_field_tool", description="Search transactions by any field/column. Available fields: country, city, card_type, merchant, merchant_category, merchant_type, currency, device, channel, is_fraud. Use this when user wants to filter by specific attributes like 'transactions from USA' or 'Visa card transactions'")
        async def search_transactions_by_field_tool(column: str, value: str, limit: int = 20):
            self.logger.info(f"Tool called: search_transactions_by_field_tool with column={column}, value={value}, limit={limit}")
            try:
                transactions = await self.provider_service.get_transactions_by_param_limit(column, value, limit, 0)

                if not transactions:
                    self.logger.warning(f"No transactions found for {column} = {value}")
                    return f"No transactions found where {column} equals '{value}'."

                result = f"Found {len(transactions)} transactions where {column} = '{value}':\n\n"
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} | Customer: {transaction.get('customer_id')} | Amount: ${transaction.get('amount')} | Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                self.logger.info(f"Successfully retrieved {len(transactions)} transactions for {column} = {value}")
                return result
            except Exception as e:
                self.logger.error(f"Error in search_transactions_by_field_tool: {str(e)}")
                return f"Error searching transactions: {str(e)}"

        @tool("get_all_transactions_by_field_tool", description="Get ALL transactions matching a specific field value (no limit). Use this when user wants a number of transactions for a field like 'all transactions from Japan' or 'all Mastercard transactions'")
        async def get_all_transactions_by_field_tool(column: str, value: str):
            self.logger.info(f"Tool called: get_all_transactions_by_field_tool with column={column}, value={value}")
            try:
                transactions = await self.provider_service.get_transactions_by_param_all(column, value)

                if not transactions:
                    self.logger.warning(f"No transactions found for {column} = {value}")
                    return f"No transactions found where {column} equals '{value}'."

                result = f"Found {len(transactions)} total transactions where {column} = '{value}':\n\n"

                self.logger.info(f"Successfully retrieved {len(transactions)} transactions for {column} = {value}")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_all_transactions_by_field_tool: {str(e)}")
                return f"Error searching transactions: {str(e)}"

        @tool("predict_transaction_fraud_tool", description="Predict if a transaction is fraudulent using the backend ML model. Use this when the user asks about fraud prediction for a specific transaction ID")
        async def predict_transaction_fraud_tool(transaction_id: str):
            self.logger.info(f"Tool called: predict_transaction_fraud_tool with transaction_id={transaction_id}")
            try:
                # Make API call to backend prediction service
                prediction_result = await self.backend_client.predict_transaction(transaction_id)

                # Format the response
                prediction = prediction_result.get('is_fraud', False)
                confidence = prediction_result.get('probability', 0.0)

                # Convert boolean to readable string
                prediction_text = "Fraud" if prediction else "Legitimate"

                result = f"🔍 Fraud Prediction Results for Transaction {transaction_id}:\n\n"
                result += f"📊 Prediction: {prediction_text}\n"
                result += f"🎯 Confidence: {confidence:.2%}\n"
              
                # Add risk assessment
                if confidence > 0.8:
                    result += f"\n⚠️ High Confidence Prediction - Recommended Action Required"
                elif confidence > 0.6:
                    result += f"\n🔍 Medium Confidence - Review Recommended"
                else:
                    result += f"\n📝 Low Confidence - Further Analysis May Be Needed"

                self.logger.info(f"Fraud prediction completed for transaction {transaction_id}: {prediction} ({confidence:.2%})")
                return result

            except ValueError as e:
                # Handle transaction not found
                self.logger.warning(f"Transaction not found: {transaction_id}")
                return f"❌ Transaction '{transaction_id}' was not found in the system. Please verify the transaction ID and try again."

            except Exception as e:
                self.logger.error(f"Error in predict_transaction_fraud_tool: {str(e)}")
                return f"❌ Unable to predict fraud for transaction {transaction_id}. Error: {str(e)}"

        @tool("check_backend_connection_tool", description="Check if the backend prediction service is available and healthy. Use this when there are connection issues or to verify backend status")
        async def check_backend_connection_tool():
            self.logger.info("Tool called: check_backend_connection_tool")
            try:
                is_healthy = await self.backend_client.health_check()

                if is_healthy:
                    result = "✅ Backend connection is healthy and ready for predictions"
                else:
                    result = "❌ Backend service is not responding. Predictions may not be available."

                self.logger.info(f"Backend health check result: {'healthy' if is_healthy else 'unhealthy'}")
                return result

            except Exception as e:
                self.logger.error(f"Error in check_backend_connection_tool: {str(e)}")
                return f"❌ Error checking backend connection: {str(e)}"

        return [get_all_transactions_tool, get_transaction_by_id_tool, get_transactions_by_customer_tool, get_fraud_transactions_tool, get_transaction_stats_tool, search_transactions_by_field_tool, get_all_transactions_by_field_tool, predict_transaction_fraud_tool, check_backend_connection_tool]

    @traceable(name="query_agent")
    async def query_agent(self, user_input: str, stream: bool = True):
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

                # Process and yield different types of updates
                if isinstance(chunk, dict):
                    for node_name, node_data in chunk.items():
                        if node_name == "agent" and isinstance(node_data, dict):
                            messages = node_data.get("messages", [])
                            if messages:
                                last_message = messages[-1]
                                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                                    # Tool call detected
                                    for tool_call in last_message.tool_calls:
                                        tool_name = tool_call.get('name', 'unknown_tool')
                                        tool_args = tool_call.get('args', {})
                                        yield {
                                            "type": "tool_call",
                                            "tool_name": tool_name,
                                            "tool_args": tool_args,
                                            "message": f"🔧 Executing tool: {tool_name}"
                                        }
                                elif hasattr(last_message, 'content') and last_message.content:
                                    # Agent response content
                                    yield {
                                        "type": "agent_thinking",
                                        "message": "🤔 Agent is analyzing..."
                                    }

                        elif node_name == "tools" and isinstance(node_data, dict):
                            # Tool execution results
                            messages = node_data.get("messages", [])
                            if messages:
                                for message in messages:
                                    if hasattr(message, 'name'):
                                        yield {
                                            "type": "tool_result",
                                            "tool_name": message.name,
                                            "message": f"✅ Tool {message.name} completed"
                                        }

                # Store the final result
                final_result = chunk

            self.logger.info(f"Streaming completed successfully")

            # Return final result
            if final_result and "agent" in final_result:
                messages = final_result["agent"]["messages"]
                if messages:
                    yield {
                        "type": "final_response",
                        "content": messages[-1].content,
                        "message": "✨ Response ready"
                    }
                    return

            yield {
                "type": "final_response",
                "content": "No data is available at the moment for your query.",
                "message": "⚠️ No response generated"
            }

        except Exception as e:
            self.logger.error(f"Error during streaming: {str(e)}")
            yield {
                "type": "error",
                "content": f"Error: {str(e)}",
                "message": "❌ An error occurred"
            }
            raise AgentException() from e
