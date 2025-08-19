# repositories/transaction_repo.py
from sqlalchemy.orm import Session
from app.schemas.transaction_schema import TransactionRequest

def get_all_transactions(db: Session):
    return db.query(TransactionRequest).all()