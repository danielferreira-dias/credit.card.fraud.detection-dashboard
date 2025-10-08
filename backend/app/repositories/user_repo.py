
from datetime import datetime
from pydantic import EmailStr
from app.exception.transaction_exceptions import DatabaseException
from app.infra.logger import setup_logger
from app.exception.user_exceptions import UserException, UserNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, desc
from app.models.user_model import Analysis, Report, User
from app.schemas.user_schema import UserCreate
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError

logger = setup_logger(__name__)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int) -> User:
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter user com ID {user_id}: {e}")
            raise UserException("Erro ao obter o utilizador da base de dados") from e
        
    async def get_user_by_email(self, user_email: EmailStr) -> User:
        try:
            result = await self.db.execute(select(User).where(User.email == user_email))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter user com ID {user_email}: {e}")
            raise UserException("Erro ao obter o utilizador da base de dados") from e
        
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            result = await self.db.execute(select(User).offset(skip).limit(limit))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter users: {e}")
            raise UserException("Erro ao obter os utilizadores da base de dados") from e

    async def create_user(self, user_data: UserCreate) -> User:
        try:
            user = User(**user_data.model_dump())
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao criar user: {e}")
            raise UserException("Erro ao criar o utilizador na base de dados") from e

    async def update_user(self, user_id: int, user_data: dict) -> User:
        try:
            user = await self.get_user(user_id)
            if user:
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                await self.db.commit()
                await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao atualizar user com ID {user_id}: {e}")
            raise UserException("Erro ao atualizar o utilizador na base de dados") from e
        
    async def delete_user(self, user_id: int) -> str:
        try:
            result = await self.db.execute(delete(User).where(User.id == user_id))
            if result.rowcount == 0:
                raise UserNotFoundException(f"User com ID {user_id} não encontrado")
            await self.db.commit()
            logger.info(f"User com ID {user_id} removida com sucesso")
            return "User deleted successfully"
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao remover user com ID {user_id}: {e}")
            raise UserException("Erro ao remover o utilizador da base de dados") from e
class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_id: int, report_content: dict) -> Report:
        """Create a new report with JSON content"""
        db_report = Report(
            user_id=user_id,
            created_at=datetime.now(),
            report_content=report_content  # SQLAlchemy handles dict -> JSON automatically
        )
        self.db.add(db_report)
        await self.db.commit()
        await self.db.refresh(db_report)
        return db_report
    
    async def get_by_user_id(self, user_id: int) -> List[Report]:
        """Get all reports for a user"""
        result = await self.db.execute(
            select(Report).where(Report.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_by_id(self, report_id: int) -> Optional[Report]:
        """Get specific report by ID"""
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_latest_user_report(self, user_id: int):
        query = (
            select(Report)
            .where(Report.user_id == user_id)
            .order_by(desc(Report.created_at))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, report_id: int) -> str:
        """Delete a report by ID"""
        try:
            result = await self.db.execute(delete(Report).where(Report.id == report_id))
            if result.rowcount == 0:
                raise DatabaseException(f"Report with ID {report_id} not found")
            await self.db.commit()
            logger.info(f"Report with ID {report_id} deleted successfully")
            return "Report deleted successfully"
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting report with ID {report_id}: {e}")
            raise DatabaseException("Error deleting report from database") from e
class AnalysisRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    
    async def create(self, user_id: int, transaction_id: str, analysis_content: dict) -> Analysis:
        """Create a new report with JSON content"""
        db_analysis = Analysis(
            user_id=user_id,
            created_at=datetime.now(),
            transaction_id=transaction_id,
            analysis_content=analysis_content  # SQLAlchemy handles dict -> JSON automatically
        )
        self.db.add(db_analysis)
        await self.db.commit()
        await self.db.refresh(db_analysis)
        return db_analysis
    
    async def get_transaction_id(self, transaction_id: str) -> Optional[Analysis]:
        """Get analysis for a specific transaction"""
        result = await self.db.execute(
            select(Analysis).where(Analysis.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()

