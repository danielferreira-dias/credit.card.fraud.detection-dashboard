# app/routers/transactions.py
import datetime
from fastapi import APIRouter, HTTPException
from typing import List

from requests import Session
from app.schemas.transaction_schema import TransactionResponse, TransactionPredictionResponse
from backend.app.service.transaction_service import TransasactionSercice

response = ""

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.get("/{transaction_id}/predict", response_model=TransactionPredictionResponse)
async def predict_transaction(db: Session, transaction_id: int):
    response = TransasactionSercice.predict_transaction_service(db, transaction_id)
    return response

@router.get("/", response_model=List[TransactionResponse])
async def list_transactions():
    response_list = TransasactionSercice.list_transactions_service()
    return response_list

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    response = TransasactionSercice.get_transaction_by_id(transaction_id)
    return response
