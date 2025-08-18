from fastapi import FastAPI
from app.schemas.transaction_schema import Transaction

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from credit-card-fraud-detection-dashboard!"}