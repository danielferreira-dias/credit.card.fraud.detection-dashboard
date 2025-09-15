from app.infra.logger import setup_logger
from app.schemas.user_schema import UserCreate, UserResponse
from app.service.user_service import UserService
from app.settings.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

logger = setup_logger(__name__)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """ Dependency to get the UserService with a database session. """
    return UserService(db)

@router.post("/", response_model=UserResponse)
async def create_user( user: UserCreate, user_service: UserService = Depends(get_user_service)):
    """
    Create a new user in the system.

    - **user**: The user details to create.

    Returns the created user's information.
    """
    logger.info(f"Creating user with email: {user.email}")
    return await user_service.create_user_service(user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user( user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Get a user by ID.

    - **user_id**: The ID of the user to retrieve.

    Returns the user's information.
    """
    logger.info(f"Getting user with ID: {user_id}")
    return await user_service.get_user_service(user_id)

@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = Query(0, ge=0, description="Number of records to skip"),limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),user_service: UserService = Depends(get_user_service)):
    """
    Get a list of users with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)

    Returns a list of users.
    """
    try:
        logger.info(f"Getting users with skip={skip}, limit={limit}")
        return await user_service.get_users_service(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int,user_data: dict,user_service: UserService = Depends(get_user_service)):
    """
    Update a user by ID.

    - **user_id**: The ID of the user to update.
    - **user_data**: Dictionary containing the fields to update.

    Returns the updated user's information.
    """
    logger.info(f"Updating user with ID: {user_id}")
    return await user_service.update_user_service(user_id, user_data)

@router.delete("/{user_id}")
async def delete_user(user_id: int,user_service: UserService = Depends(get_user_service)):
    """
    Delete a user by ID.

    - **user_id**: The ID of the user to delete.

    Returns a success message.
    """
    logger.info(f"Deleting user with ID: {user_id}")
    result = await user_service.delete_user_service(user_id)
    return {"message": result}

