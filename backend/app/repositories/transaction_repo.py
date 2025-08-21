# repositories/transaction_repo.py
from sqlalchemy.orm import Session
from app.models.transaction_model import Transaction
from app.schemas.transaction_schema import TransactionRequest
from typing import List, Optional

def get_all_transactions(db: Session) -> List[Transaction]:
    return db.query(Transaction).all()

def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def create_transaction(db: Session, transaction: TransactionRequest) -> Transaction:
    # Convert TransactionRequest to Transaction model
    db_transaction = Transaction(
        channel_large=transaction.channel_large,
        channel_medium=transaction.channel_medium,
        channel_mobile=transaction.channel_mobile,
        channel_web=transaction.channel_web,
        channel_pos=transaction.channel_pos,
        device_Android_App=transaction.device_Android_App,
        device_Safari=transaction.device_Safari,
        device_Firefox=transaction.device_Firefox,
        device_Chrome=transaction.device_Chrome,
        device_iOS_App=transaction.device_iOS_App,
        device_Edge=transaction.device_Edge,
        device_NFC_Payment=transaction.device_NFC_Payment,
        device_Magnetic_Stripe=transaction.device_Magnetic_Stripe,
        device_Chip_Reader=transaction.device_Chip_Reader,
        city_Unknown_City=transaction.city_Unknown_City,
        country_USA=transaction.country_USA,
        country_Australia=transaction.country_Australia,
        country_Germany=transaction.country_Germany,
        country_UK=transaction.country_UK,
        country_Canada=transaction.country_Canada,
        country_Japan=transaction.country_Japan,
        country_France=transaction.country_France,
        country_Singapore=transaction.country_Singapore,
        country_Nigeria=transaction.country_Nigeria,
        country_Brazil=transaction.country_Brazil,
        country_Russia=transaction.country_Russia,
        country_Mexico=transaction.country_Mexico,
        USD_converted_total_amount=transaction.USD_converted_total_amount,
        USD_converted_amount=transaction.USD_converted_amount,
        max_single_amount=transaction.max_single_amount,
        distance_from_home=transaction.distance_from_home,
        is_off_hours=transaction.is_off_hours,
        transaction_hour=transaction.transaction_hour,
        hour=transaction.hour,
        is_high_amount=transaction.is_high_amount,
        is_low_amount=transaction.is_low_amount,
        high_risk_transaction=transaction.high_risk_transaction,
        card_present=transaction.card_present,
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    transaction = get_transaction_by_id(db, transaction_id)
    if transaction:
        db.delete(transaction)
        db.commit()
    return transaction