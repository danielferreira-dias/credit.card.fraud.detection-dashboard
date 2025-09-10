from fastapi import FastAPI, Request, status
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers.transaction_router import router as transaction_router
from app.settings.database import engine
from app.models.transaction_model import Transaction
from pydantic import BaseModel

from app.exception.transaction_exceptions import TransactionsException
from app.exception.handler import transaction_handler
from app.infra.logger import setup_logger

logger = setup_logger("main")

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"

# Create database tables
Transaction.metadata.create_all(bind=engine)

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="API for detecting credit card fraud using machine learning",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

# Include routers --------------------------------------------------
app.include_router(transaction_router)

# Register exception handlers --------------------------------------------------
app.add_exception_handler(TransactionsException, transaction_handler)


@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Hello from credit-card-fraud-detection-dashboard!"}

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
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

