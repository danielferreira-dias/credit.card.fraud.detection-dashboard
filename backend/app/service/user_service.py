
from app.schemas.user_schema import UserCreate, UserResponse
from app.models.user_model import User
from app.repositories.user_repo import UserRepository
from app.exception.user_exceptions import UserNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from passlib.context import CryptContext

class UserService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user_service(self, user_data: UserCreate) -> UserResponse:
        hashed_password = self.hash_password(user_data.password)
        user_data_with_hash = UserCreate(
            email=user_data.email,
            name=user_data.name,
            password=hashed_password
        )
        user = await self.repo.create_user(user_data_with_hash)
        return self._to_response_model(user)

    async def get_user_service(self, user_id: int) -> UserResponse:
        user = await self.repo.get_user(user_id)
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return self._to_response_model(user)

    async def get_users_service(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        users = await self.repo.get_users(skip=skip, limit=limit)
        return [self._to_response_model(user) for user in users]

    async def update_user_service(self, user_id: int, user_data: dict) -> UserResponse:
        if 'password' in user_data:
            user_data['password'] = self.hash_password(user_data['password'])
        user = await self.repo.update_user(user_id, user_data)
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return self._to_response_model(user)

    async def delete_user_service(self, user_id: int) -> str:
        result = await self.repo.delete_user(user_id)
        if result == "User not found":
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return result

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def _to_response_model(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
        )