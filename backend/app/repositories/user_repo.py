
from pydantic import EmailStr
from app.exception.transaction_exceptions import DatabaseException
from app.infra.logger import setup_logger
from app.exception.user_exceptions import UserNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.user_model import User
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
            raise DatabaseException("Erro ao obter o utilizador da base de dados") from e
        
    async def get_user_by_email(self, user_email: EmailStr) -> User:
        try:
            result = await self.db.execute(select(User).where(User.email == user_email))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter user com ID {user_email}: {e}")
            raise DatabaseException("Erro ao obter o utilizador da base de dados") from e
        
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            result = await self.db.execute(select(User).offset(skip).limit(limit))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter users: {e}")
            raise DatabaseException("Erro ao obter os utilizadores da base de dados") from e

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
            raise DatabaseException("Erro ao criar o utilizador na base de dados") from e

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
            raise DatabaseException("Erro ao atualizar o utilizador na base de dados") from e
        
    async def delete_user(self, user_id: int) -> str:
        try:
            user = await self.get_user(user_id)
            if not user:
                return "User not found"
            
            result = await self.db.execute(delete(user))
            await self.db.commit()
            return "User deleted successfully"
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao remover user com ID {user_id}: {e}")
            raise DatabaseException("Erro ao remover o utilizador da base de dados") from e


        