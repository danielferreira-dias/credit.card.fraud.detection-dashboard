# repositories/transaction_repo.py
from sqlalchemy.orm import Session
from app.models.transaction_model import Transaction
from typing import List, Optional
from app.infra.logger import setup_logger
from app.exception.transaction_exceptions import DatabaseException, TransactionDuplucateError, TransactionNotFoundError
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.transaction_schema import TransactionCreate

logger = setup_logger(__name__)

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_transactions(self) -> List[Transaction]:
        try:
            transactions = self.db.query(Transaction).all()
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
        
        
        
    
    
