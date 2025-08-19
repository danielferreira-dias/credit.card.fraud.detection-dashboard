from __future__ import annotations
import datetime
from typing import List, Optional
from pydantic import BaseModel

class TransactionRequest(BaseModel):
    channel_large: int
    channel_medium: int
    device_Android_App: int
    device_Safari: int
    device_Firefox: int
    USD_converted_total_amount: float
    device_Chrome: int
    device_iOS_App: int
    city_Unknown_City: int
    country_USA: int
    country_Australia: int
    country_Germany: int
    country_UK: int
    country_Canada: int
    country_Japan: int
    country_France: int
    device_Edge: int
    country_Singapore: int
    channel_mobile: int
    country_Nigeria: int
    country_Brazil: int
    country_Russia: int
    country_Mexico: int
    is_off_hours: int
    max_single_amount: float
    USD_converted_amount: float
    channel_web: int
    is_high_amount: int
    is_low_amount: int
    transaction_hour: int
    hour: int
    device_NFC_Payment: int
    device_Magnetic_Stripe: int
    device_Chip_Reader: int
    high_risk_transaction: int
    channel_pos: int
    card_present: int
    distance_from_home: float

class TransactionPredictionResponse(BaseModel):
    is_fraud: bool
    probability: Optional[float] = None

class TransactionResponse(BaseModel):
    id: int
    country: str
    city: str
    device: str
    channel: str
    transaction_hour: int
    hour: int
    is_high_amount: bool
    is_low_amount: bool
    is_off_hours: bool
    probability: Optional[float] = None
    created_at: datetime.datetime
    card_present: bool
    distance_from_home: float
    max_single_amount: float
    USD_converted_amount: float
    USD_converted_total_amount: float
    is_high_risk_transaction: bool
    is_low_risk_transaction: bool
    is_fraud: bool



