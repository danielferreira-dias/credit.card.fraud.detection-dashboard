# repositories/transaction_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.transaction_model import Transaction
from typing import List, Optional
from app.infra.logger import setup_logger
from app.exception.transaction_exceptions import DatabaseException, TransactionDuplucateError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import delete
from app.schemas.transaction_schema import TransactionCreate
from app.schemas.filter_schema import TransactionFilter

logger = setup_logger(__name__)

class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_transaction_count(self) -> dict[str, int]:
        total_stmt = select(func.count(Transaction.transaction_id))
        fraud_stmt = select(func.count(Transaction.transaction_id)).where(Transaction.is_fraud == True)

        total_result = await self.db.execute(total_stmt)
        fraud_result = await self.db.execute(fraud_stmt)

        total = total_result.scalar()
        frauds = fraud_result.scalar()

        return {
            "total_transactions": total,
            "fraud_transactions": frauds
        }
    
    async def get_all_transactions(self, filters: TransactionFilter, limit: int, skip: int) -> List[Transaction]:
        try:
            stmt = select(Transaction)

            if filters.customer_id:
                stmt = stmt.where(Transaction.customer_id == filters.customer_id)
            if filters.country:
                stmt = stmt.where(Transaction.country.ilike(f"%{filters.country}%"))
            if filters.city:
                stmt = stmt.where(Transaction.city.ilike(f"%{filters.city}%"))
            if filters.merchant_category:
                stmt = stmt.where(Transaction.merchant_category.ilike(f"%{filters.merchant_category}%"))
            if filters.merchant:
                stmt = stmt.where(Transaction.merchant.ilike(f"%{filters.merchant}%"))
            if filters.card_type:
                stmt = stmt.where(Transaction.card_type.ilike(f"%{filters.card_type}%"))
            if filters.card_present is not None:
                stmt = stmt.where(Transaction.card_present == filters.card_present)
            if filters.channel:
                stmt = stmt.where(Transaction.channel.ilike(f"%{filters.channel}%"))
            if filters.device:
                stmt = stmt.where(Transaction.device.ilike(f"%{filters.device}%"))
            if filters.distance_from_home:
                stmt = stmt.where(Transaction.distance_from_home == filters.distance_from_home)
            if filters.high_risk_merchant is not None:
                stmt = stmt.where(Transaction.high_risk_merchant == filters.high_risk_merchant)
            if filters.start_date:
                stmt = stmt.where(Transaction.date >= filters.start_date)
            if filters.end_date:
                stmt = stmt.where(Transaction.date <= filters.end_date)
            if filters.min_amount:
                stmt = stmt.where(Transaction.amount >= filters.min_amount)
            if filters.max_amount:
                stmt = stmt.where(Transaction.amount <= filters.max_amount)
            if filters.is_fraud is not None:
                stmt = stmt.where(Transaction.is_fraud == filters.is_fraud)

            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            transactions = result.scalars().all()
            return transactions
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter transações: {e}")
            raise DatabaseException("Erro ao aceder às transações na base de dados") from e
    
    async def get_transaction_id(self, transaction_id: str) -> Transaction:
        try:
            stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
            result = await self.db.execute(stmt)
            transaction = result.scalar_one_or_none()
            logger.info(f"The transaction fetched by the database was the following: {transaction}")
            return transaction
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter transação por ID {transaction_id}: {e}")
            raise DatabaseException("Erro ao aceder à transação na base de dados") from e
    
    async def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        try:
            db_transaction = Transaction(**transaction.model_dump())
            self.db.add(db_transaction)
            await self.db.commit()
            await self.db.refresh(db_transaction)
            return db_transaction
        except SQLAlchemyError as e:
            await self.db.rollback()
            if "duplicate key" in str(e).lower():
                raise TransactionDuplucateError(name="Transição duplicada", message="Transição já existe na base de dados;")
            logger.error(f"Erro ao criar transação: {e}")
            raise DatabaseException("Erro ao criar a transação na base de dados") from e
        
    async def delete_transaction(self, transaction_id: str):
        try:
            transaction = await self.get_transaction_id(transaction_id)
            if transaction:
                await self.db.execute(delete(Transaction).where(Transaction.transaction_id == transaction_id))
                await self.db.commit()
                logger.info(f"Transação com ID {transaction_id} removida com sucesso")
            return transaction
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao remover transação com ID {transaction_id}: {e}")
            raise DatabaseException("Erro ao remover a transação na base de dados") from e
        
    async def update_transaction(self, updated_transaction: Transaction) -> Transaction:
        try:
            await self.db.commit()
            await self.db.refresh(updated_transaction)
            return updated_transaction
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao atualizar transação: {e}")
            raise DatabaseException("Erro ao atualizar a transação na base de dados") from e
        
        
        
    
    
