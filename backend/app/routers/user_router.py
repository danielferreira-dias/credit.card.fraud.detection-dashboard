from app.infra.logger import setup_logger
from app.schemas.user_schema import UserCreate, UserResponse
from app.service.user_service import UserService
from app.settings.database import get_db
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

logger = setup_logger(__name__)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """ Dependency to get the UserService with a database session. """
    return UserService(db)

@router.post("/create_user", response_model = UserResponse)
async def create_user(user: UserCreate):
    """
    Create a new user in the system.

    - **user**: The user details to create.

    Returns the created user's information.
    """
    # Here you would typically add logic to save the user to the database
    logger.info(f"Creating user with email: {user.email}")
    return UserResponse(id=1, email=user.email, name=user.name)  # Placeholder response

