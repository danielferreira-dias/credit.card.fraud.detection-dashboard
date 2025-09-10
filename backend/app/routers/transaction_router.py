# app/routers/transactions.py
from app.settings.database import get_db
from fastapi import APIRouter
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
    response = service.predict_transaction(transaction_id)
    logger.info(f"Response of router predict_transaction: {response}")
    return response
    
@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(service: TransactionService = Depends(get_transaction_service),):
    response_list = service.get_transactions()
    logger.info(f"Response of router list_transactions: {response_list}")
    return response_list

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    response = service.get_transaction_id(transaction_id)
    logger.info(f"Response of get transaction_id {transaction_id}: {response}")
    return response

@router.post("/create_transaction", response_model=ResponseWithMessage)
async def create_new_transaction(new_transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    response = service.create_transaction(new_transaction)
    return ResponseWithMessage(
        message="Transição criada com successo",
        data=response
    )

@router.delete("/{transaction_id}", response_model=ResponseWithMessage)
async def delete_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    response = service.delete_transaction(transaction_id)
    return ResponseWithMessage(
        message=f"Transaction with id {transaction_id} deleted successfully",
        data=response
    )

@router.put("/{transaction_id}", response_model=ResponseWithMessage)
async def update_transaction(transaction_id: str, updated_transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    response = service.update_transaction(transaction_id, updated_transaction)
    return ResponseWithMessage(
        message=f"Transaction with id {transaction_id} updated successfully",
        data=response
    )