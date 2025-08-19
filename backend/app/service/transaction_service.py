# services/transaction_service.py
from app.repositories.transaction_repo import get_all_transactions
from sqlalchemy.orm import Session

def list_transactions_service(db: Session):
    return get_all_transactions(db)