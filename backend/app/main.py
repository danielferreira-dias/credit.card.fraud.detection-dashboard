from app.models.user_model import User
from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from fastapi import FastAPI, status
from app.routers.transaction_router import router as transaction_router
from app.settings.database import async_engine
from app.models.transaction_model import Transaction
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.exception.transaction_exceptions import TransactionsException
from app.exception.handler import transaction_handler
from app.infra.logger import setup_logger

logger = setup_logger("main")

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"

async def create_tables():
    """Create database tables on startup"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Transaction.metadata.create_all)
        await conn.run_sync(User.metadata.create_all)

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="API for detecting credit card fraud using machine learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers --------------------------------------------------
app.include_router(transaction_router)
app.include_router(user_router)
app.include_router(auth_router)

# Register exception handlers --------------------------------------------------
app.add_exception_handler(TransactionsException, transaction_handler)

# Startup event to create tables
@app.on_event("startup")
async def startup_event():
    await create_tables()

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

