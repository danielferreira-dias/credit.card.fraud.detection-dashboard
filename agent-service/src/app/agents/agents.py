from dataclasses import dataclass
import sys
from pathlib import Path
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import create_agent
from langgraph.config import get_stream_writer
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# Add the agent-service root directory to Python path
agent_service_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(agent_service_root))

from infra.exceptions.agent_exceptions import AgentException
from infra.logging import get_agent_logger
from app.services.backend_api_client import BackendAPIClient
from app.services.vector_service import AzureVectorService, PGVectorService
from app.schemas.agent_prompt import system_prompt

import os
from dotenv import load_dotenv

load_dotenv()
logger = get_agent_logger("Agent Log", "INFO")

@dataclass
class UserContext:
    user_name: str
    user_id: int

class TransactionAgent:
    """
        This Agent is responsible to fetch knowledge vector database and database information
        providing it to a user through a chatbot
    """

    def __init__(self, model_name : str , backend_client: BackendAPIClient , vector_database : AzureVectorService | PGVectorService):
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
            temperature=1,
        )

        self.tools = self._create_tools()
        self.backend_client = backend_client
        self.vector_database = vector_database
        self.system_prompt = system_prompt

        # Store current user context (updated on each request)
        self.current_context = UserContext(user_name="Unknown", user_id=0)

        # Checkpointer will be initialized in setup()
        self.checkpointer = None
        self.agent = None
        self._checkpointer_cm = None  # Store the context manager

    async def setup(self):
        """
        Async setup method to initialize PostgresSaver and create the agent.
        Must be called after __init__ and before using the agent.
        """
        if self.checkpointer is None:
            self.logger.info("Setting up PostgresSaver for conversation checkpoints")
            try:
                # Get the connection string
                conn_string = os.getenv("DATABASE_URL")

                # Create the async context manager
                self._checkpointer_cm = AsyncPostgresSaver.from_conn_string(conn_string)

                # Enter the context manager to get the checkpointer instance
                self.checkpointer = await self._checkpointer_cm.__aenter__()

                # Catch "column already exists" errors gracefully
                try:
                    await self.checkpointer.setup()
                except Exception as setup_error:
                    if "already exists" in str(setup_error):
                        self.logger.warning(f"Database tables already exist, skipping setup: {setup_error}")
                    else:
                        raise
                
                self.agent = create_agent(
                    model=self.model,
                    tools=self.tools,
                    checkpointer=self.checkpointer,
                )

                self.logger.info("PostgresSaver setup completed successfully")

            except Exception as e:
                # Cleanup partial initialization
                self.logger.error(f"Setup failed: {e}")
                if self._checkpointer_cm is not None:
                    await self._checkpointer_cm.__aexit__(None, None, None)
                self.checkpointer = None
                self.agent = None
                self._checkpointer_cm = None
                raise
        else:
            self.logger.warning("Setup already called, skipping initialization")

    async def cleanup(self):
        """
        Cleanup method to properly close database connections.
        Should be called on application shutdown.
        """
        if self.checkpointer is not None:
            self.logger.info("Cleaning up PostgresSaver connections")

            # Exit the context manager properly
            if self._checkpointer_cm is not None:
                await self._checkpointer_cm.__aexit__(None, None, None)
                self._checkpointer_cm = None

            self.checkpointer = None
            self.logger.info("PostgresSaver cleanup completed")

    async def get_conversation_history(self, thread_id: str, limit: int = 20):
        """
        Retrieve conversation history from checkpoints for a specific thread.

        Args:
            thread_id: The thread identifier
            limit: Maximum number of messages to retrieve (default: 10)

        Returns:
            List of message dictionaries with role and content
        """
        if self.checkpointer is None:
            self.logger.warning("Checkpointer not initialized. Call setup() first.")
            return []

        try:
            config = {"configurable": {"thread_id": thread_id}}

            # Get the latest checkpoint for this thread
            checkpoint = await self.checkpointer.aget(config)

            if checkpoint is None:
                self.logger.info(f"No checkpoint found for thread {thread_id}")
                return []

            # Extract messages from checkpoint
            messages = checkpoint.get("channel_values", {}).get("messages", [])

            # Convert to simple dict format and limit
            history = []
            for msg in messages[-limit:]:
                if isinstance(msg, HumanMessage):
                    history.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    history.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    history.append({"role": "system", "content": msg.content})

            self.logger.info(f"Retrieved {len(history)} messages from thread {thread_id}")
            return history

        except Exception as e:
            self.logger.error(f"Error retrieving conversation history: {str(e)}")
            return []

    async def list_thread_checkpoints(self, thread_id: str):
        """
        List all checkpoints for a specific thread.
        Useful for debugging and understanding conversation state.

        Args:
            thread_id: The thread identifier

        Returns:
            List of checkpoint metadata
        """
        if self.checkpointer is None:
            self.logger.warning("Checkpointer not initialized. Call setup() first.")
            return []

        try:
            config = {"configurable": {"thread_id": thread_id}}
            checkpoints = list(self.checkpointer.list(config))

            self.logger.info(f"Found {len(checkpoints)} checkpoints for thread {thread_id}")
            return checkpoints

        except Exception as e:
            self.logger.error(f"Error listing checkpoints: {str(e)}")
            return []

    async def delete_thread_checkpoint(self, thread_id: str):
        """
        Delete all checkpoints for a specific thread.
        Useful when a conversation gets corrupted with incomplete tool calls.

        Args:
            thread_id: The thread identifier

        Returns:
            True if successful, False otherwise
        """
        if self.checkpointer is None:
            self.logger.warning("Checkpointer not initialized. Call setup() first.")
            return False

        try:
            # Delete checkpoint by setting it to None
            config = {"configurable": {"thread_id": thread_id}}
            await self.checkpointer.aput(config, None, {}, {})

            self.logger.info(f"Deleted checkpoints for thread {thread_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error deleting checkpoint: {str(e)}")
            return False

    def _create_tools(self):

        @tool("get_user_data", description="Retrieve user Data")
        def get_user_data():
            # Use the current context stored in the agent instance
            result = f"User Data: {self.current_context.user_name} , {self.current_context.user_id}"
            writer = get_stream_writer()
            writer(f"{result}")
            return result
        
        @tool("create_transaction_analysis", description="Create a new fraud analysis for a specific transaction. This triggers the backend to analyze transaction patterns and generate AI insights. Use when user asks to analyze a specific transaction for fraud indicators.")
        async def create_transaction_analysis(transaction_id: str):
            try:
                # Use the current context for user ID
                user_id = self.current_context.user_id
                if user_id == 0:
                    return "Error: User context not available. Please ensure you're logged in."
                
                logger.info(f'current user id -> {user_id}')

                analysis = await self.backend_client.create_transaction_analysis(
                    user_id=user_id,
                    transaction_id=transaction_id
                )

                if not analysis:
                    self.logger.warning(f"No analysis created for transaction {transaction_id}")
                    return f"Failed to create analysis for transaction {transaction_id}."

                analysis_content = analysis.get('analysis_content', {})

                # Handle both string and object analysis content
                if isinstance(analysis_content, str):
                    result = f"""Analysis created for transaction {transaction_id}:

{analysis_content}"""
                elif isinstance(analysis_content, dict):
                    # Format structured analysis content
                    result = f"""Analysis created for transaction {transaction_id}:

Title: {analysis_content.get('title', 'Transaction Fraud Analysis')}
Sentiment: {analysis_content.get('sentiment', 'Unknown')}

Key Findings:
- Severity: {analysis_content.get('key_findings', {}).get('severity', 'Unknown')}
- Finding: {analysis_content.get('key_findings', {}).get('finding', 'No specific findings')}
- Evidence: {analysis_content.get('key_findings', {}).get('evidence', 'No evidence provided')}

Critical Patterns:
{chr(10).join(f'- {pattern}' for pattern in analysis_content.get('critical_patterns', ['No critical patterns identified']))}

Recommendations:
{chr(10).join(f'- {rec}' for rec in analysis_content.get('recommendations', ['No specific recommendations']))}

Analysis:
{analysis_content.get('analysis', 'No detailed analysis available')}"""
                else:
                    result = f"Analysis created for transaction {transaction_id}, but content format is unexpected."

                writer = get_stream_writer()
                writer(f"📊 Created analysis for transaction: {transaction_id}")

                self.logger.info(f"Successfully created analysis for transaction {transaction_id}")
                return result

            except Exception as e:
                self.logger.error(f"Error in create_transaction_analysis: {str(e)}")
                return f"Error creating analysis for transaction {transaction_id}: {str(e)}"

        @tool("get_transaction_analysis", description="Retrieve an existing analysis for a transaction if it was previously created. Use when user asks about a transaction analysis that may already exist.")
        async def get_transaction_analysis(transaction_id : str):
            try:
                response = await self.backend_client.get_transaction_analysis(transaction_id=transaction_id)

                if not response:
                    self.logger.warning(f"No response received for transaction {transaction_id}")
                    return f"Unable to check analysis for transaction {transaction_id}."

                # Check if analysis exists
                analysis_exists = response.get('analysis_exists', False)

                if not analysis_exists:
                    # No analysis found - suggest creating one
                    message = response.get('message', f'No analysis found for transaction {transaction_id}')
                    suggestion = response.get('suggestion', 'Would you like to create a new fraud analysis for this transaction?')

                    result = f"""{message}

{suggestion}

I can create a comprehensive fraud analysis for this transaction if you'd like. Just ask me to "analyze transaction {transaction_id}" or "create analysis for transaction {transaction_id}" and I'll perform a detailed fraud assessment."""

                    writer = get_stream_writer()
                    writer(f"No existing analysis found for transaction {transaction_id}")

                    self.logger.info(f"No existing analysis found for transaction {transaction_id}")
                    return result

                # Analysis exists - format and return it
                analysis = response.get('analysis', {})
                analysis_content = analysis.get('analysis_content', {})

                if isinstance(analysis_content, str):
                    result = f"""Found existing analysis for transaction {transaction_id}:

{analysis_content}"""
                elif isinstance(analysis_content, dict):
                    key_findings = analysis_content.get('key_findings', {})
                    result = f"""Found existing analysis for transaction {transaction_id}:

Title: {analysis_content.get('title', 'Transaction Analysis')}
Sentiment: {analysis_content.get('sentiment', 'Unknown')}

Key Findings:
- Severity: {key_findings.get('severity', 'Unknown')}
- Finding: {key_findings.get('finding', 'No specific findings')}
- Evidence: {key_findings.get('evidence', 'No evidence provided')}

Critical Patterns:
{chr(10).join(f'- {pattern}' for pattern in analysis_content.get('critical_patterns', ['No critical patterns identified']))}

Recommendations:
{chr(10).join(f'- {rec}' for rec in analysis_content.get('recommendations', ['No specific recommendations']))}

Analysis:
{analysis_content.get('analysis', 'No detailed analysis available')}"""
                else:
                    result = f"Found existing analysis for transaction {transaction_id}, but content format is unexpected."

                writer = get_stream_writer()
                writer(f"Retrieved existing analysis for transaction {transaction_id}")

                self.logger.info(f"Successfully retrieved existing analysis for transaction {transaction_id}")
                return result

            except Exception as e:
                self.logger.error(f"Error in get_transaction_analysis: {str(e)}")
                return f"Error retrieving analysis for transaction {transaction_id}: {str(e)}"

        @tool("get_latest_report", description="Retrieve the latest report of the User when he asks to do an analysis on the latest report. To use this, you may need to fetch the user's data to get the ID.")
        async def get_latest_report(user_id: int):
            # Use the current context stored in the agent instance
            try:
                report = await self.backend_client.get_latest_report(user_id=user_id)

                if not report:
                    self.logger.warning(f"No Reports Found")
                    return f"No Reports were found."

                report_content = report.get('report_content', {})
                key_findings = report_content.get('key_findings', {})

                result = f"""Found the latest report:

Title: {report_content.get('title')}
Sentiment: {report_content.get('sentiment')}

Key Findings:
- Severity: {key_findings.get('severity')}
- Finding: {key_findings.get('finding')}
- Evidence: {key_findings.get('evidence')}

Critical Patterns:
{chr(10).join(f'- {pattern}' for pattern in report_content.get('critical_patterns', []))}

Recommendations:
{chr(10).join(f'- {rec}' for rec in report_content.get('recommendations', []))}

Analysis:
{report_content.get('analysis')}
"""

                writer = get_stream_writer()
                writer(f"📄 Retrieved latest report: {report_content.get('title')}")

                self.logger.info(f"Successfully retrieved Document")

                return result
            except Exception as e:
                self.logger.error(f"Error in get_latest_report: {str(e)}")
                return f"Error retrieving report: {str(e)}"

        @tool("search_knowledge_base", description="Search the fraud detection knowledge base for detailed insights on fraud patterns, ML model details, and transaction analysis. Use when users ask about: fraud patterns by geography/device/amount, XGBoost model training and feature importance, transaction risk indicators and thresholds, EDA insights and statistical analysis, or theoretical fraud detection concepts. Contains expert knowledge on high-risk countries (Nigeria, Russia, Mexico, Brazil), suspicious devices, velocity patterns, and model interpretation.")
        async def search_knowledge_base( query: str, limit: int = 5) -> str:
            """Search the knowledge base using semantic similarity."""
            try:
                response = await self.vector_database.hybrid_search_documents(user_query=query, k=limit)

                # Format context for LLM
                context_text = "\n\n".join([
                    f"Source: {doc['Source']}\n{doc['Content']}" 
                    for doc in response
                ])
                
                # Generate response with context
                output = f"""Use the following context to answer the question.
    
                Context:
                {context_text}

                Question: {query}

                Answer:
                """

                return output
            except AgentException as e:
                raise AgentException(message=f'Something went wrong on knowledge retrievel tool -> {e}')

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

                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')}\n"
                    result += f"   Customer: {transaction.get('customer_id')}\n"
                    result += f"   Amount: ${transaction.get('amount'):.2f} {transaction.get('currency', 'USD')}\n"
                    result += f"   Date: {transaction.get('timestamp')}\n"
                    result += f"   Merchant: {transaction.get('merchant')} ({transaction.get('merchant_category')})\n"
                    result += f"   Location: {transaction.get('city')}, {transaction.get('country')}\n"
                    result += f"   Card: {transaction.get('card_type')}\n"
                    result += f"   Channel: {transaction.get('channel')} via {transaction.get('device')}\n"
                    result += f"   Distant from Home: {'Yes' if transaction.get('distance_from_home') == 1 else 'No'}\n"
                    result += f"   High Risk Merchant: {'Yes' if transaction.get('high_risk_merchant') else 'No'}\n"
                    result += f"   Is Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}"

                    if include_predictions:
                        fraud_prob = transaction.get('fraud_probability', 0.0)
                        risk_level = 'Low' if fraud_prob < 0.3 else 'Medium' if fraud_prob < 0.7 else 'High'
                        result += f" (Fraud Probability: {fraud_prob:.2%} - {risk_level} Risk)"

                    result += "\n\n"

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

                for i, transaction in enumerate(transactions, 1):
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')}\n"
                    result += f"   Amount: ${transaction.get('amount'):.2f} {transaction.get('currency', 'USD')}\n"
                    result += f"   Date: {transaction.get('timestamp')}\n"
                    result += f"   Merchant: {transaction.get('merchant')} ({transaction.get('merchant_category')})\n"
                    result += f"   Location: {transaction.get('city')}, {transaction.get('country')}\n"
                    result += f"   Card: {transaction.get('card_type')}\n"
                    result += f"   Channel: {transaction.get('channel')} via {transaction.get('device')}\n"
                    result += f"   Distant from Home: {'Yes' if transaction.get('distance_from_home') == 1 else 'No'}\n"
                    result += f"   Is Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n\n"

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
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')}\n"
                    result += f"   Customer: {transaction.get('customer_id')}\n"
                    result += f"   Amount: ${transaction.get('amount'):.2f} {transaction.get('currency', 'USD')}\n"
                    result += f"   Date: {transaction.get('timestamp')}\n"
                    result += f"   Merchant: {transaction.get('merchant')} ({transaction.get('merchant_category')})\n"
                    result += f"   Location: {transaction.get('city')}, {transaction.get('country')}\n"
                    result += f"   Card: {transaction.get('card_type')}\n"
                    result += f"   Channel: {transaction.get('channel')} via {transaction.get('device')}\n"
                    result += f"   Distant from Home: {'Yes' if transaction.get('distance_from_home') == 1 else 'No'}\n"
                    result += f"   High Risk Merchant: {'Yes' if transaction.get('high_risk_merchant') else 'No'}\n\n"

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
                    result += f"{i}. Transaction ID: {transaction.get('transaction_id')}\n"
                    result += f"   Customer: {transaction.get('customer_id')}\n"
                    result += f"   Amount: ${transaction.get('amount'):.2f} {transaction.get('currency', 'USD')}\n"
                    result += f"   Date: {transaction.get('timestamp')}\n"
                    result += f"   Merchant: {transaction.get('merchant')} ({transaction.get('merchant_category')})\n"
                    result += f"   Location: {transaction.get('city')}, {transaction.get('country')}\n"
                    result += f"   Card: {transaction.get('card_type')}\n"
                    result += f"   Channel: {transaction.get('channel')} via {transaction.get('device')}\n"
                    result += f"   Distant from Home: {'Yes' if transaction.get('distance_from_home') == 1 else 'No'}\n"
                    result += f"   Is Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n\n"

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

                result = f"Transaction Details:\n\n"
                result += f"Transaction ID: {transaction.get('transaction_id')}\n"
                result += f"Customer ID: {transaction.get('customer_id')}\n"
                result += f"Card Number: {transaction.get('card_number')}\n"
                result += f"Card Type: {transaction.get('card_type')}\n\n"

                result += f"Amount: ${transaction.get('amount'):.2f} {transaction.get('currency', 'USD')}\n"
                result += f"Timestamp: {transaction.get('timestamp')}\n\n"

                result += f"Merchant: {transaction.get('merchant')}\n"
                result += f"Category: {transaction.get('merchant_category')}\n"
                result += f"Type: {transaction.get('merchant_type')}\n"
                result += f"High Risk: {'Yes' if transaction.get('high_risk_merchant') else 'No'}\n\n"

                result += f"Location: {transaction.get('city')} ({transaction.get('city_size')}), {transaction.get('country')}\n"
                result += f"   Distant from Home: {'Yes' if transaction.get('distance_from_home') == 1 else 'No'}\n"

                result += f"Channel: {transaction.get('channel')}\n"
                result += f"Device: {transaction.get('device')}\n"
                result += f"Card Present: {'Yes' if transaction.get('card_present') else 'No'}\n"
                result += f"Device Fingerprint: {transaction.get('device_fingerprint')}\n"
                result += f"IP Address: {transaction.get('ip_address')}\n\n"

                result += f"Transaction Hour: {transaction.get('transaction_hour')}:00\n"
                result += f"Weekend Transaction: {'Yes' if transaction.get('weekend_transaction') else 'No'}\n\n"

                velocity = transaction.get('velocity_last_hour', {})
                result += f"Velocity (Last Hour):\n"
                result += f"  - Transactions: {velocity.get('num_transactions', 0)}\n"
                result += f"  - Total Amount: ${velocity.get('total_amount', 0):.2f}\n"
                result += f"  - Unique Merchants: {velocity.get('unique_merchants', 0)}\n"
                result += f"  - Unique Countries: {velocity.get('unique_countries', 0)}\n"
                result += f"  - Max Single Amount: ${velocity.get('max_single_amount', 0):.2f}\n\n"

                result += f"Is Fraud: {'Yes' if transaction.get('is_fraud') else 'No'}\n"

                if include_predictions:
                    fraud_prob = transaction.get('fraud_probability', 0.0)
                    risk_level = 'Low' if fraud_prob < 0.3 else 'Medium' if fraud_prob < 0.7 else 'High'
                    result += f"Fraud Probability: {fraud_prob:.2%} ({risk_level} Risk)\n"

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

        return [get_user_data, get_latest_report, create_transaction_analysis, get_transaction_analysis, search_knowledge_base, get_all_transactions_tool, get_transaction_by_id_tool, get_transactions_by_customer_tool, get_fraud_transactions_tool, get_transaction_stats_tool, search_transactions_by_params_tool, get_all_transactions_count_by_params_tool, predict_transaction_fraud_tool, check_backend_connection_tool, get_all_transactions_count_tool]

    async def _stream_query(self, agent_input, thread_id: str, context: UserContext):
        """
            Stream the agent's response with progress updates

            Args:
                agent_input: Input dictionary for the agent

            Yields:
                Progress updates and final result
        """
        final_result = None

        try:
            # Update the current context before streaming
            # This ensures tools always use the latest user context
            self.current_context = context
            self.logger.info(f"Updated current_context: user_id={self.current_context.user_id}, user_name={self.current_context.user_name}")

            logger.info(f'CURRENT THREAD_ID {thread_id}')

            checkpoint = await self.checkpointer.aget({"configurable": {"thread_id": thread_id}})
            is_new_conversation = checkpoint is None or not checkpoint.get("channel_values", {}).get("messages", [])

            current_messages = checkpoint.get("channel_values", {}).get("messages", []) if checkpoint is not None else []
            logger.info(f'CURRENT MESSAGES {current_messages}')
            logger.info(f'IS NEW CONVERSATION {is_new_conversation}')

            # Add SystemMessage at the beginning for new conversations
            if is_new_conversation:
                messages = agent_input.get("messages", [])
                messages = [SystemMessage(content=self.system_prompt)] + messages
                agent_input = {"messages": messages}

            # Context is now stored in self.current_context and accessed by tools
            config = {
                'configurable': {
                    'thread_id': f"{thread_id}"
                }
            }

            # Stream with "updates" and "custom" modes to get agent progress and custom messages
            async for stream_mode, chunk in self.agent.astream(agent_input, config, stream_mode=["updates", "custom"]):
                # Process chunk using the extracted function
                async for update in self._process_stream_chunk(stream_mode, chunk):
                    yield update

                # Store the final result only from updates mode
                if stream_mode == "updates":
                    final_result = chunk

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
            raise AgentException(message=f"Error: {str(e)}") from e

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
@dataclass
class NPLOutput:
    title: str
class TitleNLP:
    def __init__(self, model_name : str):
        self.model = AzureChatOpenAI(
            azure_deployment=model_name,
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_GPT5_NANO"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=1,
        )
        self.system_prompt = "You are a NLP Model that takes in the user's query and generates a 4-5 word conversation title associated to it. The title should be concise, descriptive, and capture the main topic of the conversation."
        self.agent = create_agent(
            model = self.model,
            prompt = self.system_prompt,
            tools=[],
            response_format=NPLOutput
        )

    async def _generate_title(self, user_query: str):
        response = await self.agent.ainvoke({"messages": [ SystemMessage(f"{self.system_prompt}") ,HumanMessage(content=user_query)]})
        final_title = response.get('structured_response').title
        if final_title is None:
            return "New Conversation" 
        return final_title

class ToolOutput(BaseModel):
    tools_used: List[str] = Field(description="Name of the tools used to help writing the document")
    queries_used : List[str] = Field(description="Queries used in the Tool parameter")

class KeyFinding(BaseModel):
    finding: str = Field(description="Short description of the finding")
    evidence: str = Field(description="Evidence or data supporting the finding")
    severity: Literal["High", "Medium", "Low"] = Field(description="Severity level of the finding")

class ReportOutput(BaseModel):
    """Contact information for a person."""
    title: str = Field(description="The title of the Document")
    sentiment: Literal["Urgent", "Non Urgent"] = Field(description="The sentiment of the report")
    key_findings: KeyFinding = Field(description="Key findings of the Report")
    critical_patterns: List[str] = Field(description="Critical Patterns found")
    recommendations: List[str] = Field(description="Recommendations")
    analysis: str = Field(description="The analysis of the Agent")
    tools_used: ToolOutput = Field(description="The tool logic of the Agent")

class AnalystAgent:
    def __init__(self, model_name : str , vector_database : AzureVectorService | PGVectorService):
        self.logger = get_agent_logger("TransactionAgent", "INFO")
        self.logger.info(f"Initializing TransactionAgent with model: {model_name}")

        self.model = AzureChatOpenAI(
            azure_deployment=model_name,
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=1,
        )

        self.vector_database = vector_database
        self.tools = self.create_tools()

        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            prompt="You're a Transaction Analyst, your mission is to develop reports off a data you recieve and give your DETAILED feedback of any patterns you see. You may and I suggest you to consult your knowledge vector database to help you make your report.",
            response_format=ReportOutput
        )
    
    def create_tools(self):
        @tool("search_knowledge_base", description=("Search the fraud detection knowledge base for relevant information. ""Use this to find: fraud detection patterns, model training details, ""statistical analy methods, transaction anomaly indicators, ""risk assessment criteria, or any domain knowledge about fraud detection. ""Input should be a specific question or topic related fraud analysis."))
        async def search_knowledge_base(query: str, limit: int = 5) -> str:
            try:
                response = await self.vector_database.hybrid_search_documents(user_query=query, k=limit)

                if not response:
                    return "No relevant information found in the knowledge base for this query."

                # Format context cleanly without confusing prompts
                context_sections = []
                for i, doc in enumerate(response, 1):
                    context_sections.append(
                        f"[Knowledge Source {i}]\n"
                        f"From: {doc.get('Source', 'Unknown')}\n"
                        f"{doc.get('Content', '')}\n"
                    )
                
                return "\n".join(context_sections)
                
            except Exception as e:
                self.logger.error(f"Knowledge base search failed: {str(e)}")
                return f"Error accessing knowledge base: {str(e)}"
        
        return [search_knowledge_base]
    
    async def get_agent_report(self, backend_report : str):
        result = await self.agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": f"Report: {backend_report}"}]
        })
        return result["structured_response"]