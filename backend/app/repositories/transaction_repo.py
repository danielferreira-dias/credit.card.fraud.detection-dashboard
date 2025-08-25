# repositories/transaction_repo.py
from sqlalchemy.orm import Session
from app.models.transaction_model import Transaction
from typing import List, Optional


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_transactions(self) -> List[Transaction]:
        return self.db.query(Transaction).all()
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def create_transaction(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def delete_transaction(self, transaction_id: int) -> None:
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
    
    
