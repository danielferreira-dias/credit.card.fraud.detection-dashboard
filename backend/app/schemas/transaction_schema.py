from __future__ import annotations
import datetime
from typing import List, Optional
import numpy as np
from pydantic import BaseModel

class TransactionRequest(BaseModel):
    channel: str
    device: str
    country: str
    city: str
    transaction_hour: int
    amount: float
    total_amount: float
    max_single_amount: float
    distance_from_home: int
    currency: str
    card_present: int

    def to_numpy_array(self) -> np.ndarray:
        """
        Converts the base model fields into a NumPy array.
        """
        return np.array([
            self.channel,
            self.device,
            self.country,
            self.city,
            self.transaction_hour,
            self.amount,
            self.total_amount,
            self.max_single_amount,
            self.distance_from_home,
            self.currency,
            self.card_present
        ])

class TransactionPredictionResponse(BaseModel):
    is_fraud: int
    probability: Optional[float] = None

class TransactionResponse(BaseModel):
    costumer_id: str
    card_number: str
    timestamp: datetime.datetime
    merchant: str 
    merchant_category: str
    merchant_type: str 
    amount: float 
    currency: str
    country: str
    city: str
    city_size: str
    card_type: str
    card_present: int
    device: str
    channel: str 
    device_fingerprint: str
    ip_address: str
    distance_from_home: int
    high_risk_merchant: bool
    transaction_hour: int
    weekend_transaction: bool
    velocity_last_hour: VelocityResponse 

class VelocityResponse(BaseModel):
    num_transactions: int 
    total_amount: float
    unique_merchants: int
    unique_countries: int
    max_single_amount: float



