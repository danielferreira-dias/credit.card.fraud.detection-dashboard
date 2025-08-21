from fastapi import FastAPI
from app.routers.transaction_router import router as transaction_router
from app.settings.database import engine
from app.models.transaction_model import Transaction

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

