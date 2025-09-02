from fastapi import FastAPI, Request, status
from app.routers.transaction_router import router as transaction_router
from app.settings.database import engine
from app.models.transaction_model import Transaction
from pydantic import BaseModel

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

app.include_router(transaction_router)

@app.get("/")
def read_root():
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
    return HealthCheck(status="OK")

