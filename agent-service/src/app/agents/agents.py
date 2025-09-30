from dataclasses import dataclass
import sys
from pathlib import Path
from typing import List
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langsmith import traceable
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent
from langgraph.config import get_stream_writer
from colorama import init, Fore, Style

# Add the agent-service root directory to Python path
agent_service_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(agent_service_root))

from infra.exceptions.agent_exceptions import AgentException
from infra.logging import get_agent_logger
from app.services.backend_api_client import BackendAPIClient
from app.schemas.agent_prompt import system_prompt


import os
from dotenv import load_dotenv

load_dotenv()

# Initialize colorama for cross-platform color support
init(autoreset=True)

@dataclass
class TransactionData:
    type: str
    message: str
    content: str = ""
    tool_name: str = ""
    tool_args: str = ""

class ConversationState:
    def __init__(self, system_prompt : str):
        self.messages: List[HumanMessage | AIMessage | SystemMessage]
        self.messages = [SystemMessage(content=system_prompt)]
    
    def get_recent_messages(self, limit: int = 10):
        return self.messages[-limit:]

class TransactionAgent:
    def __init__(self, model_name : str ,backend_client: BackendAPIClient):
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
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            max_tokens=1000,
            temperature=1,
        )

        self.tools = self._create_tools()
        self.system_prompt = system_prompt
        self.backend_client = backend_client

        # Initiates State with System Messaage
        # self.agent_state = state

        # Store for chat conversations
        # self.store = InMemoryStore()

        # Store checkpoints conversation
        self.checkpointer = InMemorySaver()

        # Initialize both ReAct agent and LangGraph workflow
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            checkpointer=self.checkpointer
            # store=self.store,
        )


    def _create_tools(self):

        @tool("get_all_transactions_count_tool", description="Get COUNT OF ALL transactions matching a specific field value (no limit). Use this when user wants a number of transactions existant in the database")
        async def get_all_transactions_count_tool(column: str, value: str):
            self.logger.info(f"Tool called: get_all_transactions_count_tool with column={column}, value={value}")
            try:
                transactions = await self.backend_client.get_transaction_count()

                if not transactions:
                    self.logger.warning(f"No transactions found for {column} = {value}")
                    return f"No transactions found where {column} equals '{value}'."

                result = f"Found {transactions.get('data')} total transactions where {column} = '{value}':\n\n"

                writer = get_stream_writer()
                writer(f"{result}")

                self.logger.info(f"Successfully retrieved {len(transactions)} transactions for {column} = {value}")
                
                return result
            except Exception as e:
                self.logger.error(f"Error in get_all_transactions_count_tool: {str(e)}")
                return f"Error searching transactions: {str(e)}"

        @tool("get_all_transactions_count_by_params_tool", description="Get COUNT OF ALL transactions MATCHING a specific field value (no limit). Use this when user wants a number of transactions for a field like 'all transactions from Japan' or 'all Mastercard transactions' or 'all transactions from Japan that are fraudulent' and want the total count of them.")
        async def get_all_transactions_count_by_params_tool(column: str, value: str):
            self.logger.info(f"Tool called: get_all_transactions_count_by_params_tool with column={column}, value={value}")
            try:
                transactions = await self.backend_client.get_transaction_count_by_params(column, value)

                if not transactions:
                    self.logger.warning(f"No transactions found for {column} = {value}")
                    return f"No transactions found where {column} equals '{value}'."

                count = transactions.get('data', 0)
                result = f"Found {count} total transactions where {column} = '{value}'"

                writer = get_stream_writer()
                writer(f"{result}")

                self.logger.info(f"Successfully retrieved count of {count} transactions for {column} = {value}")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_all_transactions_count_by_params_tool: {str(e)}")
                return f"Error searching transactions: {str(e)}"
        
        @tool("get_all_transactions_tool", description="LIST all Transactions available in the database, use this when the user asks to see all transactions or wants a complete list, LIMITED to 20 results; User has the option to INCLUDE or NOT the predictions with the result")
        async def get_all_transactions_tool(limit: int = 20, skip: int = 0, include_predictions : bool = False):
            self.logger.info(f"Tool called: get_all_transactions_tool with limit={limit}, skip={skip}, include_predictions={include_predictions}")
            try:
                transactions = await self.backend_client.get_transactions(limit=limit, skip=skip, include_predictions=include_predictions)

                if not transactions:
                    self.logger.info("No transactions found in database")
                    return "No transactions were found."

                result = f"Here are {len(transactions)} transactions (showing {skip+1}-{skip+len(transactions)}):\n\n"
                writer = get_stream_writer()

                if include_predictions:
                    for i, transaction in enumerate(transactions, 1):
                        fraud_prob = transaction.get('fraud_probability', 0.0)
                        risk_level = 'Low Probability' if fraud_prob < 0.3 else 'Medium Probability' if fraud_prob < 0.7 else 'High Probability'
                        result += f"{i}. Transaction ID: {transaction.get('transaction_id')} — Customer: {transaction.get('customer_id')} — Amount: ${transaction.get('amount')} — Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}, with a probability of {fraud_prob} ({risk_level})\n"
                else:
                    for i, transaction in enumerate(transactions, 1):
                        result += f"{i}. Transaction ID: {transaction.get('transaction_id')} — Customer: {transaction.get('customer_id')} — Amount: ${transaction.get('amount')} — Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"


                writer(result)
                self.logger.info(f"Successfully retrieved {len(transactions)} transactions")
                
                return result
            except Exception as e:
                self.logger.error(f"Error in get_all_transactions_tool: {str(e)}")
                raise AgentException() from e

        @tool("get_transactions_by_customer_tool", description="LIST all transactions for a specific customer ID, use this when the user asks about a customer's transaction history, limited to 20 results;")
        async def get_transactions_by_customer_tool(customer_id: str, limit: int = 20, skip: int = 0):
            self.logger.info(f"Tool called: get_transactions_by_customer_tool with customer_id={customer_id}")
            try:
                transactions = await self.backend_client.get_transactions_by_customer(customer_id, limit, skip)

                if not transactions:
                    self.logger.warning(f"No transactions found for customer ID: {customer_id}")
                    return f"No transactions found for customer ID '{customer_id}'."

                result = f"Transaction history for customer {customer_id} ({len(transactions)} transactions):\n\n"
                writer = get_stream_writer()

                writer(f"Results \n")
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} — Amount: ${transaction.get('amount')} — Date: {transaction.get('timestamp')} — Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                writer(f"{result}")
                self.logger.info(f"Successfully retrieved {len(transactions)} transactions for customer: {customer_id}")
                
                return result
            except Exception as e:
                self.logger.error(f"Error in get_transactions_by_customer_tool: {str(e)}")
                raise AgentException() from e

        @tool("get_fraud_transactions_tool", description="LIST all fraudulent transactions, use this when the user asks about fraud cases or suspicious transactions, limited to 20 results;")
        async def get_fraud_transactions_tool(is_fraud: bool = True, limit: int = 20, skip: int = 0):
            self.logger.info("Tool called: get_fraud_transactions_tool")
            try:
                transactions = await self.backend_client.get_fraud_transactions(is_fraud, limit, skip)

                if not transactions:
                    fraud_type = "fraudulent" if is_fraud else "legitimate"
                    self.logger.info(f"No {fraud_type} transactions found in database")
                    return f"No {fraud_type} transactions found."

                fraud_type = "Fraudulent" if is_fraud else "Legitimate"
                result = f"{fraud_type} transactions found ({len(transactions)} total):\n\n"
                writer = get_stream_writer()

                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} — Customer: {transaction.get('customer_id')} — Amount: ${transaction.get('amount')} — Date: {transaction.get('timestamp')}\n"

                writer(f"{result}")
                self.logger.info(f"Successfully retrieved {len(transactions)} {fraud_type.lower()} transactions")
                return result
            except Exception as e:
                self.logger.error(f"Error in get_fraud_transactions_tool: {str(e)}")
                raise AgentException() from e

        @tool("get_transaction_stats_tool", description="Get basic STATISTICS about transactions including total count, fraud rate, and amounts, use this when the user asks for transaction statistics or summary")
        async def get_transaction_stats_tool():
            self.logger.info("Tool called: get_transaction_stats_tool")
            try:
                stats = await self.backend_client.get_transactions_stats()

                result = f"Transaction Statistics:\n\n"
                result += f"Total Transactions: {stats.get('total_transactions', 0):,}\n"
                result += f"Fraudulent Transactions: {stats.get('fraudulent_transactions', 0):,}\n"
                result += f"Fraud Rate: {stats.get('fraud_rate', 0):.2f}%\n"
                result += f"Average Transaction Amount: ${stats.get('avg_amount', 0):.2f}\n"
                result += f"Total Max Transaction Amount: ${stats.get('max_amount', 0):,.2f}\n"
                result += f"Total Min Transaction Amount: ${stats.get('min_amount', 0):,.2f}\n"

                self.logger.info(f"Successfully retrieved transaction statistics: total={stats.get('total_transactions', 0)}, fraud_rate={stats.get('fraud_rate', 0):.2f}%")
                writer = get_stream_writer()
                writer(f"{result}")

                return result
            except Exception as e:
                self.logger.error(f"Error in get_transaction_stats_tool: {str(e)}")
                raise AgentException() from e

        @tool("predict_transaction_fraud_tool", description="PREDICT if a transaction is fraudulent using the backend ML model. Use this when the user asks about fraud prediction for a specific transaction ID")
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
                writer = get_stream_writer()
                writer(f"{result}")
                return result

            except ValueError as e:
                # Handle transaction not found
                self.logger.warning(f"Transaction not found: {transaction_id}")
                return f"❌ Transaction '{transaction_id}' was not found in the system. Please verify the transaction ID and try again."

            except Exception as e:
                self.logger.error(f"Error in predict_transaction_fraud_tool: {str(e)}")
                return f"❌ Unable to predict fraud for transaction {transaction_id}. Error: {str(e)}"

        @tool("search_transactions_by_params_tool", description="Search transactions by any field/column. Available fields: country, city, card_type, merchant, merchant_category, merchant_type, currency, device, channel, is_fraud. Use this when user wants to filter by specific attributes like 'transactions from USA' or 'Visa card transactions', limited by 20 results;")
        async def search_transactions_by_params_tool(column: str, value: str, limit: int = 20, skip: int = 0):
            self.logger.info(f"Tool called: search_transactions_by_params_tool with column={column}, value={value}, limit={limit}")
            try:
                transactions = await self.backend_client.get_transactions_by_field(column, value, limit, skip)

                if not transactions:
                    self.logger.warning(f"No transactions found for {column} = {value}")
                    return f"No transactions found where {column} equals '{value}'."

                result = f"Found {len(transactions)} transactions where {column} = '{value}':\n\n"
                writer = get_stream_writer()
                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')} — Customer: {transaction.get('customer_id')} — Amount: ${transaction.get('amount')} — Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                writer(f"{result}")
                self.logger.info(f"Successfully retrieved {len(transactions)} transactions for {column} = {value}")
                
                return result
            except Exception as e:
                self.logger.error(f"Error in search_transactions_by_params_tool: {str(e)}")
                return f"Error searching transactions: {str(e)}"

        @tool("get_transaction_by_id_tool", description="Get a specific transaction by its ID, use this when the user asks about a particular transaction, User has the option to INCLUDE or NOT the predictions with the result")
        async def get_transaction_by_id_tool(transaction_id: str , include_predictions : bool = False):
            self.logger.info(f"Tool called: get_transaction_by_id_tool with transaction_id={transaction_id} with include_predictions as {include_predictions}")
            try:
                transaction = await self.backend_client.get_transaction_by_id(transaction_id, include_predictions)

                if not transaction:
                    self.logger.warning(f"Transaction not found for ID: {transaction_id}")
                    return f"Transaction with ID '{transaction_id}' was not found."

                writer = get_stream_writer()

                result = f"Transaction Details:\n"
                result += f"ID: {transaction.get('transaction_id')}\n"
                result += f"Customer ID: {transaction.get('customer_id')}\n"
                result += f"Amount: ${transaction.get('amount')}\n"
                result += f"Timestamp: {transaction.get('timestamp')}\n"
                result += f"Is Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"
                if include_predictions:
                    fraud_prob = transaction.get('fraud_probability', 0.0)
                    risk_level = 'Low Probability' if fraud_prob < 0.3 else 'Medium Probability' if fraud_prob < 0.7 else 'High Probability'
                    result += f"Is Fraud: {'Yes' if transaction.get('fraud_probability') else '0.0'}, with a probability of {fraud_prob} ({risk_level}\n"
                writer(f"{result}")

                self.logger.info(f"Successfully retrieved transaction details for ID: {transaction_id}")
                
                return result
            except Exception as e:
                self.logger.error(f"Error in get_transaction_by_id_tool: {str(e)}")
                raise AgentException() from e
    
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
                writer = get_stream_writer()
                writer(f"{result}")
                return result

            except Exception as e:
                self.logger.error(f"Error in check_backend_connection_tool: {str(e)}")
                return f"❌ Error checking backend connection: {str(e)}"

        return [get_all_transactions_tool, get_transaction_by_id_tool, get_transactions_by_customer_tool, get_fraud_transactions_tool, get_transaction_stats_tool, search_transactions_by_params_tool, get_all_transactions_count_by_params_tool, predict_transaction_fraud_tool, check_backend_connection_tool, get_all_transactions_count_tool]

    @traceable(name="query_agent")
    async def query_agent(self, user_input: str, thread_id : str ,stream: bool = True):
        """
            Ensures the first message is the System Prompt initialized, then adds the user Input as HumanMessage
            It then invokes the agent by running once with the input and returning the final structured output;

            Args:
                user_input: User's query string
                stream: Whether to stream the response (default: True)
        """
        try:
            if stream:
                return await self._stream_query({"messages": [HumanMessage(content=user_input)]}, thread_id)
            else:
                result = await self.agent.ainvoke({"messages": [HumanMessage(content=user_input)]}, {'configurable': {'thread_id': f"{thread_id}"}})
                return result
        except Exception as e:
            self.logger.error(f"Error during agent invocation: {str(e)}")
            raise AgentException() from e

    async def _stream_query(self, agent_input, thread_id: str):
        """
            Stream the agent's response with progress updates

            Args:
                agent_input: Input dictionary for the agent

            Yields:
                Progress updates and final result
        """
        final_result = None

        try:
            # Stream with "updates" and "custom" modes to get agent progress and custom messages
            async for stream_mode, chunk in self.agent.astream(agent_input, {'configurable': {'thread_id': f"{thread_id}"}} ,stream_mode=["updates", "custom"]):
                # Process chunk using the extracted function
                async for update in self._process_stream_chunk(stream_mode, chunk):
                    yield update

                # Store the final result only from updates mode
                if stream_mode == "updates":
                    final_result = chunk

            checkpoints = self.checkpointer.list({"configurable": {"thread_id": "1"}})
            self.logger.info(f'Current checkpoints -> {checkpoints}')
            process_checkpoints(checkpoints)

            # Return final result
            if final_result and "agent" in final_result:
                messages = final_result["agent"]["messages"]
                # self.agent_state.messages.append(AIMessage(content=messages[-1].content))
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

    async def _process_stream_chunk(self, stream_mode, chunk):
        """
        Process individual stream chunks and yield appropriate updates

        Args:
            stream_mode: The mode of the stream ("custom" or "updates")
            chunk: The chunk data to process

        Yields:
            Processed stream updates
        """
        # Handle custom stream messages from writer() calls
        if stream_mode == "custom":
            yield {
                "type": "tool_progress",
                "content": str(chunk),
                "message": f"📄 Tool Update: {chunk}"
            }
            return

        # Process and yield different types of updates
        if stream_mode == "updates" and isinstance(chunk, dict):
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
                                    "message": f"🔧 Executing tool: {tool_name} with the following {tool_args}"
                                }
                        elif hasattr(last_message, 'content') and last_message.content:
                            # Agent response content
                            yield {
                                "type": "agent_thinking",
                                "message": f"🤔 {last_message.content}"
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

# Define a function to process checkpoints
def process_checkpoints(checkpoints):
    """
    Processes a list of checkpoints and displays relevant information.

    Parameters:
        checkpoints (list): A list of checkpoint tuples to process.

    Returns:
        None

    This function processes a list of checkpoints.
    It iterates over the checkpoints and displays the following information for each checkpoint:
    - Timestamp
    - Checkpoint ID
    - Messages associated with the checkpoint
    """
    logger = get_agent_logger(name='CheckPoint Logger')

    logger.info(f"{Fore.YELLOW}{'='*60}")

    for idx, checkpoint_tuple in enumerate(checkpoints):
        # Extract key information about the checkpoint
        checkpoint = checkpoint_tuple.checkpoint
        messages = checkpoint["channel_values"].get("messages", [])

        # Display checkpoint information
        logger.info(f"{Fore.MAGENTA}Checkpoint ID: {checkpoint['id']}")

        # Display checkpoint messages
        for message in messages:
            if isinstance(message, HumanMessage):
                logger.info(
                    f"{Fore.CYAN}👤 User: {Style.BRIGHT}{message.content}{Style.RESET_ALL} "
                    f"{Fore.BLUE}(Message ID: {message.id})"
                )
            elif isinstance(message, AIMessage):
                logger.info(
                    f"{Fore.GREEN}🤖 Agent: {Style.BRIGHT}{message.content}{Style.RESET_ALL} "
                    f"{Fore.BLUE}(Message ID: {message.id})"
                )

        logger.info("")

    logger.info(f"{Fore.YELLOW}{'='*60}")