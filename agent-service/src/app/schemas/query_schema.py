from datetime import datetime
from typing import Optional
from pydantic import BaseModel
class QuerySchema(BaseModel):
    query : str
    thread_id: Optional[str] = None
    
class QueryResponse(BaseModel):
    query: str
    agent_type: str

class TransactionFilter(BaseModel):
    """Schema for filtering transactions."""
    customer_id: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    merchant: Optional[str] = None
    merchant_category: Optional[str] = None
    card_type: Optional[str] = None
    card_present: Optional[int] = None
    channel: Optional[str] = None
    device: Optional[str] = None
    distance_from_home: Optional[int] = None
    high_risk_merchant: Optional[bool] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_fraud: Optional[bool] = None



