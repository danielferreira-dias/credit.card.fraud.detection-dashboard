# app/routers/transactions.py
import datetime

from fastapi.exceptions import RequestValidationError
import joblib
from psycopg2 import IntegrityError
from app.settings.database import get_db
from fastapi import APIRouter, HTTPException
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.transaction_schema import ResponseWithMessage, TransactionCreate, TransactionResponse, TransactionPredictionResponse
from app.service.transaction_service import TransactionService
from app.infra.logger import setup_logger

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

logger = setup_logger(__name__)

# --- dependencies ------------------------
def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

# --- router ------------------------

@router.get("/{transaction_id}/predict", response_model=TransactionPredictionResponse)
async def predict_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    response = service.predict_transaction_service(transaction_id)
    logger.info(f"Response of router predict_transaction: {response}")
    return response
    
@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(service: TransactionService = Depends(get_transaction_service),):
    response_list = service.list_transactions_service()
    logger.info(f"Response of router list_transactions: {response_list}")
    return response_list

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    response = service.get_transaction_by_id(transaction_id)
    logger.info(f"Response of get transaction_id {transaction_id}: {response}")
    return response

@router.post("/create_transaction", response_model=ResponseWithMessage)
async def create_new_transaction(new_transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    response = service.create_transaction(new_transaction)
    return ResponseWithMessage(
        message="Transição criada com successo",
        data=response
    )