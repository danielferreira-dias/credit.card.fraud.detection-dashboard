from contextlib import asynccontextmanager
from typing import Optional
from app.agents.agents import AnalystAgent, TitleNLP, TransactionAgent, UserContext
from app.services.database_provider import ProviderService
from app.services.backend_api_client import BackendAPIClient
from app.services.vector_service import AzureVectorService, PGVectorService, EmbeddingModel
from app.database.transactions_db import TransactionsDB
from app.schemas.query_schema import QuerySchema
from fastapi import FastAPI, status, Depends
from fastapi.responses import StreamingResponse
from infra.logging.logger import get_agent_logger
from langchain_core.messages import HumanMessage, SystemMessage
from app.schemas.agent_prompt import system_prompt
from pydantic import BaseModel
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

logger = get_agent_logger("Router Log", "INFO")
class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"

class AgentState:
    def __init__(self):
        self.agent : Optional[TransactionAgent] = None
        self.agent_nlp : Optional[TitleNLP] = None
        self.agent_analyst : Optional[AnalystAgent] = None

agent_state = AgentState()

#---------------------------------------

def get_transactions_db() -> TransactionsDB:
    """Dependency to provide TransactionsDB instance"""
    return TransactionsDB()

def get_backend_client() -> BackendAPIClient:
    return BackendAPIClient()

def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel(model_id="sentence-transformers/all-MiniLM-L6-v2")

def get_azure_vector_database(embedding_model : EmbeddingModel = Depends(get_embedding_model)) -> AzureVectorService:
    return AzureVectorService(embedding_model=embedding_model)

def get_pg_vector_database(embedding_model : EmbeddingModel = Depends(get_embedding_model)) -> PGVectorService:
    return PGVectorService(embedding_model=embedding_model)

def get_provider_service(db: TransactionsDB = Depends(get_transactions_db)) -> ProviderService:
    """Dependency to provide ProviderService instance"""
    return ProviderService(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle with startup and shutdown logic.

    FastAPI's lifespan context manager allows initialization of expensive resources
    (database connections, ML models, API clients) once at startup, rather than on
    every request. This pattern ensures efficient resource management and proper cleanup.

    Lifecycle Flow:
    ---------------
    1. STARTUP (Before yield):
       - Initialize Azure OpenAI LLM model
       - Create BackendAPIClient for transaction data
       - Initialize TransactionAgent with LangGraph workflow
       - Setup PostgreSQL checkpoint saver for conversation persistence
       - Store agent in global state for request handlers

    2. RUNTIME (During yield):
       - Application runs and handles incoming requests
       - All request handlers access the pre-initialized agent via dependency injection

    3. SHUTDOWN (After yield):
       - Close PostgreSQL checkpoint saver connections
       - Cleanup agent resources (prevents connection leaks)
       - Graceful shutdown of background tasks

    Benefits:
    ---------
    - Single agent instance shared across all requests (memory efficient)
    - Database connection pooling maintained throughout app lifetime
    - Prevents resource leaks and zombie connections
    - Faster response times (no repeated initialization)

    Args:
        app (FastAPI): The FastAPI application instance

    Yields:
        None: Control returned to FastAPI to run the application
    """

    # STARTUP: Runs once when server starts
    logger.info("🚀 Starting up...")
    
    # Initialize expensive resources
    model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "Llama-4-Maverick-17B-128E-Instruct-FP8")
    model_name_nlp = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT5_NANO", "Llama-4-Maverick-17B-128E-Instruct-FP8")
    backend_client = get_backend_client()

    # Create dependencies manually (not using FastAPI dependency injection in lifespan)
    embedding_model = get_embedding_model()
    azure_vector_database = AzureVectorService(embedding_model=embedding_model)

    agent_instance = TransactionAgent(
        model_name=model_name,
        backend_client=backend_client,
        vector_database=azure_vector_database
    )
    agent_instance_nlp = TitleNLP(
        model_name=model_name_nlp,
    )
    agent_analyst_instance = AnalystAgent(
        model_name=model_name,
        vector_database=azure_vector_database
    )
    await agent_instance.setup() 
    agent_state.agent = agent_instance
    agent_state.agent_nlp = agent_instance_nlp
    agent_state.agent_analyst = agent_analyst_instance
    
    logger.info("✅ Ready to handle requests")
    
    # YIELD: Server runs and handles requests
    yield 
    
    # SHUTDOWN: Runs once when server stops
    logger.info("🛑 Shutting down...")
    if agent_state.agent is not None:
        await agent_state.agent.cleanup() 
    logger.info("👋 Goodbye")

app = FastAPI(
    title="Agent Service",
    description="It's the service that the backend uses to communicate ",
    version="1.0.0",
    lifespan=lifespan
)

#---------------------------------------

def get_transaction_agent() -> TransactionAgent:
    """Dependency to provide TransactionAgent instance"""
    if agent_state.agent is None:
        raise RuntimeError("Agent not initialized")
    return agent_state.agent

def get_nlp_agent() -> TitleNLP:
    """Dependency to provide TransactionAgent instance"""
    if agent_state.agent is None:
        raise RuntimeError("Agent not initialized")
    return agent_state.agent_nlp

def get_analyst_agent() -> AnalystAgent:
    """Dependency to provide TransactionAgent instance"""
    if agent_state.agent_analyst is None:
        raise RuntimeError("Agent not initialized")
    return agent_state.agent_analyst 

#---------------------------------------

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Hello from credit-card-fraud-detection-dashboard!"}


class StreamException(Exception):
    def __init__(self, message="An exception in Streaming has happened"):
        super().__init__(message)

@app.get("/user_report")
async def get_agent_report(report_text: str, analyst_agent: AnalystAgent = Depends(get_analyst_agent)):
    if report_text is None:
        return "Report was not generated due to empty Report Text"
    
    return await analyst_agent.get_agent_report(backend_report=report_text)

@app.post("/user_message/stream")
async def stream_agent_query(user_query: QuerySchema , agent: TransactionAgent = Depends(get_transaction_agent), nlp_agent : TitleNLP = Depends(get_nlp_agent)):
    """
    Stream AI agent responses with real-time progress updates via Server-Sent Events (SSE).

    This endpoint enables interactive conversations with the LangGraph-powered fraud detection agent.
    It streams agent reasoning, tool executions, and final responses in real-time, providing visibility
    into the agent's decision-making process.

    Request Body (QuerySchema):
    ---------------------------
    {
        "query": "Show me all fraudulent transactions from Japan",
        "thread_id": "user-123-session-456"  // Optional, defaults to "default"
    }
    Response Format:
    ---------------
    Content-Type: text/event-stream
    Stream events are sent in Server-Sent Events format:
    event: token
    data: {"type": "tool_call", "tool_name": "search_transactions_by_params_tool", "message": "🔧 Executing tool..."}
    event: token
    data: {"type": "tool_progress", "content": "Found 5 transactions...", "message": "📄 Tool Update"}
    event: token
    data: {"type": "final_response", "content": "Here are the fraudulent transactions...", "message": "✨ Response ready"}
    Event Types:
    -----------
    - `tool_call`: Agent is invoking a tool (e.g., database query, fraud prediction)
    - `tool_progress`: Intermediate results from tool execution
    - `tool_result`: Tool completed successfully
    - `agent_thinking`: Agent reasoning or planning next steps
    - `final_response`: Complete agent answer (last event in stream)
    - `error`: Exception occurred during processing

    Conversation Persistence:
    ------------------------
    - Each `thread_id` maintains isolated conversation history in PostgreSQL
    - LangGraph automatically loads previous messages from checkpoints
    - Agent has full context of conversation across requests
    - Use same `thread_id` for multi-turn conversations
    - Use different `thread_id` for separate conversation sessions
    """

    # Get thread_id from request body, default to "default" if not provided
    thread_id = user_query.thread_id if user_query.thread_id else "default"
    user_id = user_query.user_id if user_query.user_id else None
    user_name = user_query.user_name if user_query.user_name else 'Daniel Dias'
    context = UserContext(user_id=user_id, user_name=user_name)
    logger.info(f'CURRENT USER CONTEXT -> {context}')
    
    if user_id is None:
        raise StreamException(message="User ID is None")

    async def generate_stream():
        try:
            # Only generate title if requested (for new conversations)
            if user_query.generate_title:
                chat_title = await nlp_agent._generate_title(user_query.query)

                # Send the chat title as the first event
                title_data = {
                    'type': 'chat_title',
                    'content': chat_title,
                    'message': 'Chat title generated'
                }
                yield (
                    "event: token\n"
                    f"data: {json.dumps(title_data)}\n\n"
                )

            agent_input = {"messages": [HumanMessage(content=f"{user_name}: " + user_query.query)]}
            async for update in agent._stream_query(agent_input=agent_input, thread_id=thread_id, context=context):
                # Send each update as Server-Sent Event
                yield (
                    "event: token\n"
                    f"data: {json.dumps(update)}\n\n"
                )
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming

        except Exception as e:
            error_data = {
                'type': 'error',
                'content': f'Error: {str(e)}',
                'message': 'An error occurred'
            }
            logger.info(f"The current error was -> {error_data['content']}")
            yield (
                "event: error\n"
                f"data: {json.dumps(error_data)}\n\n"
            )

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/conversation_history/{thread_id}")
async def get_conversation_history( thread_id: str, limit: int = 20, agent: TransactionAgent = Depends(get_transaction_agent)):
    """
    Retrieve conversation history for a specific thread from checkpoints.

    Args:
        thread_id: The conversation thread identifier
        limit: Maximum number of messages to retrieve (default: 10)

    Returns:
        JSON response with conversation history
    """
    logger.info(f"Retrieving conversation history for thread: {thread_id}")

    try:
        history = await agent.get_conversation_history(thread_id, limit)
        return {
            "thread_id": thread_id,
            "message_count": len(history),
            "messages": history
        }
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return {
            "thread_id": thread_id,
            "error": str(e),
            "messages": []
        }

@app.get("/thread_checkpoints/{thread_id}")
async def get_thread_checkpoints( thread_id: str, agent: TransactionAgent = Depends(get_transaction_agent)):
    """
    List all checkpoints for a specific thread.
    Useful for debugging conversation state.

    Args:
        thread_id: The conversation thread identifier

    Returns:
        JSON response with checkpoint metadata
    """
    logger.info(f"Listing checkpoints for thread: {thread_id}")

    try:
        checkpoints = await agent.list_thread_checkpoints(thread_id)

        # Convert checkpoints to serializable format
        checkpoint_info = []
        for cp_tuple in checkpoints:
            checkpoint_info.append({
                "checkpoint_id": cp_tuple.checkpoint.get("id"),
                "thread_id": cp_tuple.config.get("configurable", {}).get("thread_id"),
                "message_count": len(cp_tuple.checkpoint.get("channel_values", {}).get("messages", []))
            })

        return {
            "thread_id": thread_id,
            "checkpoint_count": len(checkpoint_info),
            "checkpoints": checkpoint_info
        }
    except Exception as e:
        logger.error(f"Error listing checkpoints: {str(e)}")
        return {
            "thread_id": thread_id,
            "error": str(e),
            "checkpoints": []
        }

@app.get( "/health", tags=["healthcheck"], summary="Perform a Health Check", response_description="Return HTTP Status Code 200 (OK)", status_code=status.HTTP_200_OK, response_model=HealthCheck)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    logger.info("Health check endpoint called")
    return HealthCheck(status="OK")