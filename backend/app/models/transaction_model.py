from sqlalchemy import Column, Integer, Float, Boolean, DateTime, String
from sqlalchemy.sql import func
from app.settings.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Channel information
    channel_large = Column(Integer, default=0)
    channel_medium = Column(Integer, default=0)
    channel_mobile = Column(Integer, default=0)
    channel_web = Column(Integer, default=0)
    channel_pos = Column(Integer, default=0)
    
    # Device information
    device_Android_App = Column(Integer, default=0)
    device_Safari = Column(Integer, default=0)
    device_Firefox = Column(Integer, default=0)
    device_Chrome = Column(Integer, default=0)
    device_iOS_App = Column(Integer, default=0)
    device_Edge = Column(Integer, default=0)
    device_NFC_Payment = Column(Integer, default=0)
    device_Magnetic_Stripe = Column(Integer, default=0)
    device_Chip_Reader = Column(Integer, default=0)
    
    # Location information
    city_Unknown_City = Column(Integer, default=0)
    country_USA = Column(Integer, default=0)
    country_Australia = Column(Integer, default=0)
    country_Germany = Column(Integer, default=0)
    country_UK = Column(Integer, default=0)
    country_Canada = Column(Integer, default=0)
    country_Japan = Column(Integer, default=0)
    country_France = Column(Integer, default=0)
    country_Singapore = Column(Integer, default=0)
    country_Nigeria = Column(Integer, default=0)
    country_Brazil = Column(Integer, default=0)
    country_Russia = Column(Integer, default=0)
    country_Mexico = Column(Integer, default=0)
    
    # Amount and transaction details
    USD_converted_total_amount = Column(Float)
    USD_converted_amount = Column(Float)
    max_single_amount = Column(Float)
    distance_from_home = Column(Float)
    
    # Time information
    is_off_hours = Column(Integer, default=0)
    transaction_hour = Column(Integer)
    hour = Column(Integer)
    
    # Risk indicators
    is_high_amount = Column(Integer, default=0)
    is_low_amount = Column(Integer, default=0)
    high_risk_transaction = Column(Integer, default=0)
    card_present = Column(Integer, default=0)
    
    # Fraud prediction
    is_fraud = Column(Boolean, default=False)
    fraud_probability = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Human-readable fields for display
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    device = Column(String(100), nullable=True)
    channel = Column(String(100), nullable=True)
