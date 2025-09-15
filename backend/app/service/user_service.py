
from app.schemas.user_schema import UserCreate, UserResponse
from app.models.user_model import User
from app.repositories.user_repo import UserRepository
from app.exception.user_exceptions import UserNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user_service(self, user_data: UserCreate) -> UserResponse:
        return self._to_response_model(self.db.create_user(user_data)) 

    async def get_user_service(self, email: str) -> UserResponse:
        user = await self.repo.get_user_by_email(email)
        if user is None:
            raise UserNotFoundException(f"User with email {email} not found")
        return self._to_response_model(user)

    async def update_user(self, user_id: int, user_data: UserCreate) -> UserResponse:
        user = await self.repo.update_user(user_id, user_data.dict(exclude_unset=True))
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return self._to_response_model(user)

    async def delete_user(self, user_id: int) -> str:
        success = await self.repo.delete_user(user_id)
        if not success:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return "User deleted successfully"

    @staticmethod
    def hash_password(password: str) -> str:
        pass
        # Implement password hashing logic here
    
    @staticmethod
    def _to_response_model(user: User) -> UserResponse:
        # Convert User model instance to UserResponse schema instance
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
        )