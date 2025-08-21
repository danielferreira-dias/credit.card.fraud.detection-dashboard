# app/routers/transactions.py
import datetime
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.transaction_schema import TransactionRequest, TransactionResponse, TransactionPredictionResponse

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

test_transaction = TransactionRequest(
    channel_large=1,
    channel_medium=1,
    device_Android_App=1,
    device_Safari=1,
    device_Firefox=1,
    USD_converted_total_amount=100,
    device_Chrome=1,
    device_iOS_App=1,
    city_Unknown_City=1,
    country_USA=1,
    country_Australia=1,
    country_Germany=1,
    country_UK=1,
    country_Canada=1,
    country_Japan=1,
    country_France=1,
    device_Edge=1,
    country_Singapore=1,
    channel_mobile=1,
    country_Nigeria=1,
    country_Brazil=1,
    country_Russia=1,
    country_Mexico=1,
    is_off_hours=1,
    max_single_amount=100,
    USD_converted_amount=100,
    channel_web=1,
    is_high_amount=1,
    is_low_amount=1,
    transaction_hour=1,
    hour=1,
    device_NFC_Payment=1,
    device_Magnetic_Stripe=1,
    device_Chip_Reader=1,
    high_risk_transaction=1,
    channel_pos=1,
    card_present=1,
    distance_from_home=1,
)

response = TransactionResponse (
        id=1,
        country="USA",
        city="New York",
        device="Android",
        channel="Web",
        transaction_hour=1,
        hour=1,
        is_high_amount=True,
        is_low_amount=False,
        is_off_hours=False,
        probability=0.95,
        created_at=datetime.datetime.now(),
        card_present=True,
        distance_from_home=100,
        max_single_amount=100,
        USD_converted_amount=100,
        USD_converted_total_amount=100,
        is_high_risk_transaction=True,
        is_low_risk_transaction=False,
        is_fraud=True,
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
async def create_transaction(transaction: TransactionRequest):
    return response

@router.delete("/{transaction_id}", response_model=TransactionResponse)
async def delete_transaction(transaction_id: int):
    return response