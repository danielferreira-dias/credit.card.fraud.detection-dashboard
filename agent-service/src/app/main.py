from app.agents.agents import TransactionAgent
from app.services.database_provider import ProviderService
from app.services.backend_api_client import BackendAPIClient
from app.database.transactions_db import TransactionsDB
from app.schemas.query_schema import QuerySchema
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.responses import StreamingResponse
from infra.logging.logger import get_agent_logger
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

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="API for detecting credit card fraud using machine learning",
    version="1.0.0"
)

#---------------------------------------

def get_transactions_db() -> TransactionsDB:
    """Dependency to provide TransactionsDB instance"""
    return TransactionsDB()

def get_backend_client() -> BackendAPIClient:
    return BackendAPIClient()

def get_provider_service(db: TransactionsDB = Depends(get_transactions_db)) -> ProviderService:
    """Dependency to provide ProviderService instance"""
    return ProviderService(db)

def get_transaction_agent(provider_service: ProviderService = Depends(get_provider_service), backend_client: BackendAPIClient = Depends(get_backend_client)) -> TransactionAgent:
    """Dependency to provide TransactionAgent instance"""
    model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    return TransactionAgent(model_name, provider_service, backend_client)

#---------------------------------------

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Hello from credit-card-fraud-detection-dashboard!"}

@app.post("/user_message")
async def query_agent(user_query: QuerySchema, agent: TransactionAgent = Depends(get_transaction_agent)):
    """Normal query route that returns agent response"""
    try:
        return await agent.query_agent(user_query.query, stream=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.post("/user_message/stream")
async def stream_agent_query(user_query: QuerySchema, agent: TransactionAgent = Depends(get_transaction_agent)):
    """Streaming route that yields agent progress updates"""

    async def generate_stream():
        try:
            # Prepare input for agent
            agent_input = {"messages": agent.history_messages + [{"role": "human", "content": user_query.query}]}
            logger.info(f'Agent Input -> {agent_input}')

            async for update in agent._stream_query(agent_input):
                logger.info(f'Agent update -> {update}')
                # Send each update as Server-Sent Event
                yield (
                    "event: token\n"
                    f"data: {json.dumps(update)}\n\n"
                )
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming

        except Exception as e:
            error_update = {
                "type": "error",
                "content": f"Error: {str(e)}",
                "message": "❌ An error occurred"
            }
            yield (
                "event: error\n"
                f"data: {json.dumps(error_update)}\n\n"
            )

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

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