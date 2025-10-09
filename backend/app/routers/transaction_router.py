# app/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.settings.database import get_db
from app.schemas.transaction_schema import ResponseWithMessage, TransactionCreate, TransactionResponse, TransactionPredictionResponse
from app.service.transaction_service import TransactionService
from app.infra.logger import setup_logger
from app.schemas.filter_schema import TransactionFilter
from app.service.user_service import AnalysisService
from app.repositories.user_repo import AnalysisRepository
import aiohttp
import os 
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

logger = setup_logger(__name__)

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8001")

# --- dependencies ------------------------
def get_transaction_service(db: AsyncSession = Depends(get_db)) -> TransactionService:
    """ Dependency to get the TransactionService with a database session. """
    return TransactionService(db)

def get_analysis_service(db: AsyncSession = Depends(get_db)) -> AnalysisService:
    """ Dependency to get the ReportService with a ReportRepository. """
    analysis_repo = AnalysisRepository(db)
    return AnalysisService(analysis_repo)

# --- router ------------------------

@router.get("/count", response_model=ResponseWithMessage)
async def count_transactions(service: TransactionService = Depends(get_transaction_service)):
    """
    Count the total number of transactions in the database.

    Returns the total count of transactions.
    """
    response = await service.get_transactions_qt()
    return ResponseWithMessage(
        message=f"There's currently {response} transactions in the database",
        data=response
    )

@router.get("/filtered/count", response_model=ResponseWithMessage)
async def count_filtered_transactions(filters: TransactionFilter = Depends(), service: TransactionService = Depends(get_transaction_service)):
    """
    Count the number of transactions in the database that match the given filters.
    - **filters**: Optional filters to apply (e.g., date range, amount range, merchant).
    Returns the count of transactions matching the criteria.
    """
    response = await service.get_filtered_transactions_qt(filters)
    return ResponseWithMessage(
        message=f"There's currently {response} transactions in the database matching the given filters",
        data=response
    )

@router.get("/stats")
async def transaction_stats(service: TransactionService = Depends(get_transaction_service)):
    """
    Get statistics about transactions, including total count, fraudulent count, and non-fraudulent count.

    Returns a summary of transaction statistics.
    """
    response = await service.get_transaction_stats()
    logger.info(f"Response of router transaction_stats: {response}")
    return {
        "total_transactions": response.get("total_transactions", 0),
        "fraudulent_transactions": response.get("fraudulent_transactions", 0),
        "fraud_rate": response.get("fraud_rate", 0.0),
        "average_amount": response.get("avg_amount", 0.0),
        "max_amount": response.get("max_amount", 0),
        "min_amount": response.get("min_amount", 0)
    }

@router.get("/{transaction_id}/predict", response_model=TransactionPredictionResponse)
async def predict_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)):
    """
    Predict if a transaction is fraudulent based on its ID.

    - **transaction_id**: The ID of the transaction to predict.

    Returns the prediction result along with the transaction details.
    """
    response = await service.predict_transaction(transaction_id)
    logger.info(f"Response of router predict_transaction: {response}")
    return response
    
@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(filters: TransactionFilter = Depends(), include_predictions : bool = False, limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0) ,service: TransactionService = Depends(get_transaction_service),):
    """
    List transactions with optional filtering and pagination.
    
    - **filters**: Optional filters to apply (e.g., date range, amount range, merchant).
    - **limit**: Maximum number of transactions to return (default is 20, maximum is 100).
    - **skip**: Number of transactions to skip for pagination (default is 0).
    
    Returns a list of transactions matching the criteria."""
    response_list = await service.get_transactions(filters, limit, skip, include_predictions)
    return response_list

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, include_predictions : bool = False, service: TransactionService = Depends(get_transaction_service)):
    """
    Get a transaction by its ID.
    
    - **transaction_id**: The ID of the transaction to retrieve.
    
    Returns the transaction details.
    """
    response = await service.get_transaction_id(transaction_id)
    logger.info(f"Response of get transaction_id {transaction_id}: {response}")
    return response

@router.post("/create_transaction", response_model=ResponseWithMessage)
async def create_new_transaction(new_transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    """
    Create a new transaction.

    - **new_transaction**: The transaction data to create.  

    Returns a message indicating the success of the operation along with the created transaction data.
    """
    response = await service.create_transaction(new_transaction)
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
    response = await service.delete_transaction(transaction_id)
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

    response = await service.update_transaction(transaction_id, updated_transaction)
    return ResponseWithMessage(
        message=f"Transaction with id {transaction_id} updated successfully",
        data=response
    )

@router.get("/analysis/transaction_id")
async def get_analysis_by_transaction_id(transaction_id: str, analysis_service: AnalysisService = Depends(get_analysis_service), service: TransactionService = Depends(get_transaction_service)):
    try:
        analysis = await analysis_service.get_analysis(transaction_id=transaction_id)

    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis creation for transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis creation") from e


@router.post("/analysis/{user_id}")
async def create_report(user_id: int, transaction_id: str, analysis_service: AnalysisService = Depends(get_analysis_service), service: TransactionService = Depends(get_transaction_service)):
    try:
        # Check if analysis already exists for this transaction
        existent_analysis = await analysis_service.get_analysis(transaction_id=transaction_id)
        if existent_analysis is not None:
            logger.info(f"Returning existing analysis for transaction {transaction_id}")
            return existent_analysis

        # Get transaction data with fraud predictions - this will raise an exception if transaction doesn't exist
        transaction_data = await service.get_transaction_id(transaction_id=transaction_id, include_predictions=True)
        if not transaction_data:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

        # Format transaction data for agent analysis
        analysis = {'transaction': transaction_data}
        final_analysis = analysis_service._format_stats_to_text(analysis)

        # Call agent service for analysis
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{AGENT_SERVICE_URL}/user_report?report_text={final_analysis}") as response:
                response.raise_for_status()
                agent_response = await response.json()

        # Create and store new analysis
        new_analysis = await analysis_service.create_analysis(
            user_id=user_id,
            transaction_id=transaction_id,
            analysis_content=agent_response
        )

        logger.info(f"Created new analysis for transaction {transaction_id}")
        return new_analysis

    except aiohttp.ClientError as e:
        logger.error(f"Agent service error for transaction {transaction_id}: {e}")
        raise HTTPException(status_code=503, detail="Agent service is currently unavailable") from e
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis creation for transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis creation") from e
