
from http.client import HTTPException
from pydantic import EmailStr
from app.schemas.user_schema import UserCreate, UserRegisterSchema, UserResponse, UserSchema
from app.models.user_model import User
from app.repositories.user_repo import UserRepository
from app.exception.user_exceptions import UserCredentialInvalid, UserDuplicateException, UserNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple
from app.security.password_utils import hash_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user_service(self, user_data: UserRegisterSchema) -> UserResponse:
        if user_data.password != user_data.confirm_password:
            raise UserCredentialInvalid('Password is not matching the confirm password')
        new_user = await self.repo.get_user_by_email(user_data.email)
        if new_user:
            raise UserDuplicateException(
                message="User with this email already exists"
            )
        hashed_password = hash_password(user_data.password)
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
    
    async def get_user_service_email(self, email: EmailStr) -> UserResponse:
        user = await self.repo.get_user_by_email(email)
        if user is None:
            raise UserNotFoundException(f"User with email {email} not found")
        return self._to_response_model(user)

    async def get_users_service(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        users = await self.repo.get_users(skip=skip, limit=limit)
        return [self._to_response_model(user) for user in users]

    async def update_user_service(self, user_id: int, user_data: dict) -> UserResponse:
        if 'password' in user_data:
            user_data['password'] = hash_password(user_data['password'])
        user = await self.repo.update_user(user_id, user_data)
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return self._to_response_model(user)

    async def delete_user_service(self, user_id: int) -> str:
        user: User = await self.repo.get_user(user_id)
        return await self.repo.delete_user(user.id)
    
    @staticmethod
    def _to_response_model(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
        )