# repositories/transaction_repo.py
from sqlalchemy.orm import Session
from app.models.transaction_model import Transaction
from typing import List, Optional
from app.infra.logger import setup_logger
from app.exception.transaction_exceptions import DatabaseException, TransactionDuplucateError
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.transaction_schema import TransactionCreate
from app.schemas.filter_schema import TransactionFilter

logger = setup_logger(__name__)

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_transaction_count(self) -> dict[str, int]:
        total = self.db.query(Transaction).count()
        frauds = self.db.query(Transaction).filter(Transaction.is_fraud == True).count()
        
        return {
            "total_transactions": total,
            "fraud_transactions": frauds
        }
    
    def get_all_transactions(self, filters: TransactionFilter, limit: int, skip: int) -> List[Transaction]:
        try:
            query = self.db.query(Transaction)

            if filters.customer_id:
                query = query.filter(Transaction.customer_id == filters.customer_id)
            if filters.country:
                query = query.filter(Transaction.country.ilike(f"%{filters.country}%"))
            if filters.city:
                query = query.filter(Transaction.city.ilike(f"%{filters.city}%"))
            if filters.merchant_category:
                query = query.filter(Transaction.merchant_category.ilike(f"%{filters.merchant_category}%"))
            if filters.merchant:
                query = query.filter(Transaction.merchant.ilike(f"%{filters.merchant}%"))
            if filters.card_type:
                query = query.filter(Transaction.card_type.ilike(f"%{filters.card_type}%"))
            if filters.card_present is not None:
                query = query.filter(Transaction.card_present == filters.card_present)
            if filters.channel:
                query = query.filter(Transaction.channel.ilike(f"%{filters.channel}%"))
            if filters.device:
                query = query.filter(Transaction.device.ilike(f"%{filters.device}%"))
            if filters.distance_from_home:
                query = query.filter(Transaction.distance_from_home == filters.distance_from_home)
            if filters.high_risk_merchant is not None:
                query = query.filter(Transaction.high_risk_merchant == filters.high_risk_merchant)
            if filters.start_date:
                query = query.filter(Transaction.date >= filters.start_date)
            if filters.end_date:
                query = query.filter(Transaction.date <= filters.end_date)
            if filters.min_amount:
                query = query.filter(Transaction.amount >= filters.min_amount)
            if filters.max_amount:
                query = query.filter(Transaction.amount <= filters.max_amount)
            if filters.merchant:
                query = query.filter(Transaction.merchant.ilike(f"%{filters.merchant}%"))
            if filters.is_fraud is not None:
                query = query.filter(Transaction.is_fraud == filters.is_fraud)

            transactions = query.offset(skip).limit(limit).all()
            return transactions
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter transações: {e}")
            raise DatabaseException("Erro ao aceder às transações na base de dados") from e
    
    def get_transaction_id(self, transaction_id: str) -> Transaction:
        try:
            transaction = self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
            logger.info(f"The transaction fetched by the database was the following: {transaction}")
            return transaction
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter transação por ID {transaction_id}: {e}")
            raise DatabaseException("Erro ao aceder à transação na base de dados") from e
    
    def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        try:
            transaction = Transaction(**transaction.model_dump())
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        except SQLAlchemyError as e:
            if "duplicate key" in str(e).lower():
                raise TransactionDuplucateError(name="Transição duplicada", message="Transição já existe na base de dados;")
            logger.error(f"Erro ao criar transação: {e}")
            raise DatabaseException("Erro ao criar a transação na base de dados") from e
        
    def delete_transaction(self, transaction_id: str):
        try:
            transaction = self.get_transaction_id(transaction_id)
            logger.info(f"Transação com ID {transaction_id} removida com sucesso")
            self.db.delete(transaction)
            self.db.commit()

        except SQLAlchemyError as e:
            logger.error(f"Erro ao remover transação com ID {transaction_id}: {e}")
            raise DatabaseException("Erro ao remover a transação na base de dados") from e
        
    def update_transaction(self, updated_transaction: Transaction) -> Transaction:
        try:
            self.db.commit()
            self.db.refresh(updated_transaction)
            return updated_transaction
        except SQLAlchemyError as e:
            logger.error(f"Erro ao atualizar transação: {e}")
            raise DatabaseException("Erro ao atualizar a transação na base de dados") from e
        
        
        
    
    
