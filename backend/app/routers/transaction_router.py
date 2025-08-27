# app/routers/transactions.py
import datetime

import joblib
from app.settings.database import get_db
from fastapi import APIRouter, HTTPException
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.transaction_schema import TransactionResponse, TransactionPredictionResponse
from app.service.transaction_service import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

# --- dependencies ------------------------
def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

# --- router ------------------------

@router.get("/{transaction_id}/predict", response_model=TransactionPredictionResponse)
async def predict_transaction(service: TransactionService = Depends(get_transaction_service), transaction_id: int = None):
    response = service.predict_transaction_service(transaction_id)
    return response

@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(service: TransactionService = Depends(get_transaction_service),):
    response_list = service.list_transactions_service()
    return response_list

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(service: TransactionService = Depends(get_transaction_service), transaction_id: str = ""):
    response = service.get_transaction_by_id(transaction_id)
    return response
