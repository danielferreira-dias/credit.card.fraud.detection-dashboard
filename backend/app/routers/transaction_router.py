# app/routers/transactions.py
import datetime
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.transaction_schema import TransactionRequest, TransactionResponse, TransactionPredictionResponse

response = ""

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.get("/", response_model=List[TransactionResponse])
async def list_transactions():
    response_list = []
    response_list.append(response)

    if response_list is None:
        raise HTTPException(status_code=404, detail="Transactions not found")

    return response_list

@router.get("/{transaction_id}/predict", response_model=TransactionPredictionResponse)
async def predict_transaction(transaction_id: int):
    response = TransactionPredictionResponse(
        is_fraud=True,
        probability=0.95,
    )
    if not response:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return response

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    if not response:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return response

@router.post("/", response_model=TransactionResponse)
async def create_transaction(transaction):
    return response

@router.delete("/{transaction_id}", response_model=TransactionResponse)
async def delete_transaction(transaction_id: int):
    return response