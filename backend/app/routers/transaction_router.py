# app/routers/transactions.py
from fastapi import Query
from app.settings.database import get_db
from fastapi import APIRouter
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.transaction_schema import ResponseWithMessage, TransactionCreate, TransactionResponse, TransactionPredictionResponse
from app.service.transaction_service import TransactionService
from app.infra.logger import setup_logger
from app.schemas.filter_schema import TransactionFilter

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

logger = setup_logger(__name__)

# --- dependencies ------------------------
def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    """ Dependency to get the TransactionService with a database session. """
    return TransactionService(db)

# --- router ------------------------

@router.get("transactions/count", response_model=ResponseWithMessage)
async def count_transactions(service: TransactionService = Depends(get_transaction_service)):
    """
    Count the total number of transactions in the database.

    Returns the total count of transactions.
    """
    response = service.get_transactions_qt()
    return ResponseWithMessage(
        message=f"There's currently {response} transactions in the database",
        data=None
    )

@router.get("/{transaction_id}/predict", response_model=TransactionPredictionResponse)
async def predict_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    """
    Predict if a transaction is fraudulent based on its ID.

    - **transaction_id**: The ID of the transaction to predict.

    Returns the prediction result along with the transaction details.
    """
    response = service.predict_transaction(transaction_id)
    logger.info(f"Response of router predict_transaction: {response}")
    return response
    
@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(filters: TransactionFilter = Depends(), limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0) ,service: TransactionService = Depends(get_transaction_service),):
    """
    List transactions with optional filtering and pagination.
    
    - **filters**: Optional filters to apply (e.g., date range, amount range, merchant).
    - **limit**: Maximum number of transactions to return (default is 20, maximum is 100).
    - **skip**: Number of transactions to skip for pagination (default is 0).
    
    Returns a list of transactions matching the criteria."""
    response_list = service.get_transactions(filters, limit, skip)
    logger.info(f"Response of router list_transactions: {response_list}")
    return response_list

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    """
    Get a transaction by its ID.
    
    - **transaction_id**: The ID of the transaction to retrieve.
    
    Returns the transaction details.
    """
    response = service.get_transaction_id(transaction_id)
    logger.info(f"Response of get transaction_id {transaction_id}: {response}")
    return response

@router.post("/create_transaction", response_model=ResponseWithMessage)
async def create_new_transaction(new_transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    """
    Create a new transaction.

    - **new_transaction**: The transaction data to create.  

    Returns a message indicating the success of the operation along with the created transaction data.
    """
    response = service.create_transaction(new_transaction)
    return ResponseWithMessage(
        message="Transição criada com successo",
        data=response
    )

@router.delete("/{transaction_id}", response_model=ResponseWithMessage)
async def delete_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    """
    Delete a transaction by its ID.
    
    - **transaction_id**: The ID of the transaction to delete.
    
    Returns a message indicating the success of the operation along with the deleted transaction data.
    """
    response = service.delete_transaction(transaction_id)
    return ResponseWithMessage(
        message=f"Transaction with id {transaction_id} deleted successfully",
        data=response
    )

@router.put("/{transaction_id}", response_model=ResponseWithMessage)
async def update_transaction(transaction_id: str, updated_transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    """
    Update an existing transaction.
    
    - **transaction_id**: The ID of the transaction to update.
    - **updated_transaction**: The updated transaction data.
    
    Returns a message indicating the success of the operation along with the updated transaction data.
    """

    response = service.update_transaction(transaction_id, updated_transaction)
    return ResponseWithMessage(
        message=f"Transaction with id {transaction_id} updated successfully",
        data=response
    )
