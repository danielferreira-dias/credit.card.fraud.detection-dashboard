from sqlalchemy import Column, Integer, Float, Boolean, DateTime, String
from sqlalchemy.sql import func
from app.settings.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    card_number = Column(String(32), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    merchant_category = Column(String(100), nullable=True)
    merchant_type = Column(String(100), nullable=True)
    merchant = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    city_size = Column(String(50), nullable=True)
    card_type = Column(String(50), nullable=True)
    card_present = Column(Boolean, default=False)
    device = Column(String(100), nullable=True)
    channel = Column(String(100), nullable=True)
    device_fingerprint = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    distance_from_home = Column(Float, nullable=True)
    high_risk_merchant = Column(Boolean, default=False)
    transaction_hour = Column(Integer, nullable=True)
    weekend_transaction = Column(Boolean, default=False)
    velocity_last_hour = Column(Integer, nullable=True)
    is_fraud = Column(Boolean, default=False)


