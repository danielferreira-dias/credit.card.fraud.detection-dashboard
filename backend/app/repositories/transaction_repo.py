# repositories/transaction_repo.py
from sqlalchemy.orm import Session
from app.models.transaction_model import Transaction
from typing import List, Optional
from app.infra.logger import setup_logger
from app.exception.transaction_exceptions import DatabaseException, TransactionDuplucateError, TransactionNotFoundError
from sqlalchemy.exc import SQLAlchemyError

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
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        try:
            transaction = self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
            return transaction
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter transação por ID {transaction_id}: {e}")
            raise DatabaseException("Erro ao aceder à transação na base de dados") from e
    
    def create_transaction(self, transaction: Transaction) -> Transaction:
        try:
            existing_transaction = self.get_transaction_by_id(transaction.transaction_id)
            if existing_transaction:   
                logger.warning(f"Transação com ID {transaction.transaction_id} já existe")
                raise TransactionDuplucateError("Transação com este ID já existe na base de dados")
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar transação: {e}")
            raise DatabaseException("Erro ao criar a transação na base de dados") from e
        
    def delete_transaction(self, transaction_id: str):
        try:
            transaction = self.get_transaction_by_id(transaction_id)
            if transaction is None:
                logger.warning(f"Transação com ID {transaction_id} não encontrada para remoção")
                raise TransactionNotFoundError("Transação não encontrada na base de dados")
            
            logger.info(f"Transação com ID {transaction_id} removida com sucesso")
            self.db.delete(transaction)
            self.db.commit()

        except SQLAlchemyError as e:
            logger.error(f"Erro ao remover transação com ID {transaction_id}: {e}")
            raise DatabaseException("Erro ao remover a transação na base de dados") from e
        
    def update_transaction(self, transaction_id: str, updated_transaction: Transaction) -> Transaction:
        try:
            transaction = self.get_transaction_by_id(transaction_id)

            if transaction is None:
                logger.warning(f"Transação com ID {transaction_id} não encontrada para atualização")
                raise TransactionNotFoundError("Transação não encontrada na base de dados")
            
            for key, value in updated_transaction.__dict__.items():
                if key != "transaction_id" and value is not None:
                    setattr(transaction, key, value)

            logger.info(f"Transação com ID {transaction_id} atualizada com sucesso")
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        
        except SQLAlchemyError as e:
            logger.error(f"Erro ao atualizar transação com ID {transaction_id}: {e}")
            raise DatabaseException("Erro ao atualizar a transação na base de dados") from e
        
        
        
    
    
