from typing import List
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, String
from app.settings.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
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
    distance_from_home = Column(Integer, nullable=True)
    high_risk_merchant = Column(Boolean, default=False)
    transaction_hour = Column(Integer, nullable=True)
    weekend_transaction = Column(Boolean, default=False)
    velocity_last_hour = Column(JSONB, nullable=True)
    is_fraud = Column(Boolean, default=False)

    analysis = relationship("Analysis", back_populates="transaction")

    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, amount={self.amount}, is_fraud={self.is_fraud}), customer_id={self.customer_id}, merchant={self.merchant}, timestamp={self.timestamp}, country={self.country}, city={self.city}, card_type={self.card_type}, channel={self.channel}, device={self.device}), card_present={self.card_present}, high_risk_merchant={self.high_risk_merchant}, weekend_transaction={self.weekend_transaction}, transaction_hour={self.transaction_hour}, distance_from_home={self.distance_from_home}, velocity_last_hour={self.velocity_last_hour}, currency={self.currency}, merchant_category={self.merchant_category}, merchant_type={self.merchant_type}, ip_address={self.ip_address}, device_fingerprint={self.device_fingerprint}, card_number={self.card_number}"


# Ordem EXATA das features (usa estes nomes como colunas no DataFrame)
FEATURE_COLUMNS: List[str] = [
    "channel_medium","device_Android App","device_Safari","device_Firefox",
    "USD_converted_total_amount","device_Chrome","device_iOS App","city_Unknown City",
    "country_USA","country_Australia","country_Germany","country_UK","country_Canada",
    "country_Japan","country_France","device_Edge","country_Singapore","channel_mobile",
    "country_Nigeria","country_Brazil","country_Russia","country_Mexico","is_off_hours",
    "max_single_amount","USD_converted_amount","channel_web","is_high_amount","is_low_amount",
    "transaction_hour","hour","device_NFC Payment","device_Magnetic Stripe",
    "device_Chip Reader","high_risk_transaction","channel_pos","suspicious_device","card_present",
    "distance_from_home",
]

