from fastapi import FastAPI
from app.routers.transaction import router as transaction_router

app = FastAPI()
app.include_router(transaction_router)

@app.get("/")
def read_root():
    return {"message": "Hello from credit-card-fraud-detection-dashboard!"}

