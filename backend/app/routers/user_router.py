import aiohttp
from app.infra.logger import setup_logger
from app.schemas.user_schema import UserRegisterSchema, UserResponse
from app.service.user_service import ReportService, UserService
from app.settings.database import get_db
from app.service.stats_cache_service import StatsCacheService
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8001")

logger = setup_logger(__name__)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """ Dependency to get the UserService with a database session. """
    return UserService(db)

def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    """ Dependency to get the UserService with a database session. """
    return ReportService(db)

def get_cache_service(db: AsyncSession = Depends(get_db)) -> StatsCacheService:
    """ Dependency to get the UserService with a database session. """
    return StatsCacheService(db)

@router.post("/", response_model=UserResponse)
async def create_user( user: UserRegisterSchema, user_service: UserService = Depends(get_user_service)):
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
async def delete_user(user_id: int , user_service: UserService = Depends(get_user_service)):
    """
    Delete a user by ID.

    - **user_id**: The ID of the user to delete.

    Returns a success message.
    """
    logger.info(f"Deleting user with ID: {user_id}")
    user = await user_service.get_user_service(user_id)
    result = await user_service.delete_user_service(user.id)
    return {"message": result}

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """
    WebSocket endpoint for testing real-time communication.

    - **client_id**: The ID of the client connecting
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for client: {client_id}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from client {client_id}: {data}")
            response = f"Echo from server: {data} (client #{client_id})"
            await websocket.send_text(response)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client: {client_id}")

@router.post("/reports/{user_id}")
async def create_report(user_id: int , report_service: ReportService = Depends(get_report_service), cache_service: StatsCacheService = Depends(get_cache_service)):
    report = {}
    try:
        # Add await here!
        report['geral'] = await cache_service.get_geral_stats(force_refresh=False)
        report['overview'] = await cache_service.get_stats_overview(force_refresh=False)

        final_report = report_service._format_stats_to_text(report)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{AGENT_SERVICE_URL}/user_report?report_text={final_report}") as response:
                response.raise_for_status()
                data = await response.json()

        logger.info(f'REPORT DATA -> {data}')
        return await report_service.create_report(user_id=user_id, report_content=data)
    
    except HTTPException as e:
        raise HTTPException(status_code=500, detail="Something happened with the Agent Service") from e
