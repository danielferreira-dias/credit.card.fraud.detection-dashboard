from datetime import datetime
from typing import List
import json
from app.infra.logger import setup_logger
from app.routers.auth_router import get_security_manager, get_user_service
from app.security.security import SecurityManager
from app.schemas.message_schema import ConversationCreate, ConversationResponse, MessageResponse
from app.settings.database import get_db
from app.service.message_service import ConversationService, MessageService, websocket_conversation_handle
from app.repositories.message_repo import ConversationRepository, MessageRepository
from app.ws.connection_manager import ConnectionManager
from app.schemas.websocket_schema import WebSocketMessage
from app.service.websocket_auth_service import authenticate_websocket
from app.service.websocket_message_handler import websocket_message_handler
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix = '/chat',
    tags =['chat']
)

logger = setup_logger(__name__)
security = HTTPBearer()

# --- Dependencies ---------------------------

def get_message_service(db: AsyncSession = Depends(get_db)):
    return MessageService(db, get_message_repo(db), get_conversation_repository(db))

def get_message_repo(db: AsyncSession = Depends(get_db)):
    return MessageRepository(db)

def get_conversation_service(db: AsyncSession = Depends(get_db)):
    return ConversationService(get_conversation_repository(db), get_message_repo(db), get_user_service(db))

def get_conversation_repository(db: AsyncSession = Depends(get_db)):
    return ConversationRepository(db)


def get_connection_manager():
    return ConnectionManager()

# --- Router ---------------------------

@router.websocket("/ws/agent/{user_id}")
async def agent_websocket_endpoint( websocket: WebSocket, user_id: int, token: str,  conversation_id: int = None, connection_manager: ConnectionManager = Depends(get_connection_manager), conversation_service: ConversationService = Depends(get_conversation_service), message_service: MessageService = Depends(get_message_service), security_manager: SecurityManager = Depends(get_security_manager)):
    """WebSocket endpoint for chat with AI agent"""
    try:
        await authenticate_websocket(websocket=websocket , security_manager=security_manager , token=token, connection_manager=connection_manager, user_id=user_id)
    except Exception as auth_error:
        logger.error(f"Authentication failed for user {user_id}: {str(auth_error)}")
        await websocket.close(code=4001, reason="Unauthorized: Invalid token")
        return
    
    # Initialize or retrieve conversation
    current_conversation_id = conversation_id
    thread_id = None
    try:
        current_conversation_id, thread_id = await websocket_conversation_handle(conversation_service=conversation_service, current_conversation_id=conversation_id  ,user_id=user_id)
        # Send conversation details to client
        conversation_info = WebSocketMessage(
            type="conversation_started",
            content=f"Connected to conversation {current_conversation_id} (Thread: {thread_id})"
        )
        await websocket.send_text(json.dumps(conversation_info.to_dict()))

        while True:
            await websocket_message_handler( websocket = websocket , message_service = message_service, conversation_service = conversation_service, convo_id = current_conversation_id, thread_id = thread_id )

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info(f"Agent chat disconnected for user {user_id}, conversation {current_conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        await websocket.close(code=1011, reason="Internal server error")

@router.post('/{conversation_id}/message')
async def send_message(role : str , conversation : ConversationCreate, conversation_service: ConversationService = Depends(get_conversation_service), message_service : MessageService = Depends(get_message_service) , token: str = Depends(security), security_manager: SecurityManager = Depends(get_security_manager), ) -> ConversationResponse:
    # This is a protected router, so let's check for a token;
    payload = await security_manager.verify_token(token)

    # Let's check if the conversation_id exists
    if not conversation.conversation_id:
        conversation_id = await conversation_service.create_conversation(conversation)
    else:
        conversation_id = conversation.conversation_id
    
    # Let's create the message and the respective conversation and store in the database;
    await conversation_service.add_message_to_conversation(conversation, conversation_id)
    await message_service.create_message(conversation_id, conversation.content)
    
    # Serve it to the frontend
    return ConversationResponse(
        name = payload['user'].get('name'),
        role = role,
        content = conversation.content,
        created_at = datetime.now()
    )

@router.get('/{user_id}', response_model = MessageResponse)
async def get_messages( user_id : int,  token: str = Depends(security), conversation_service: ConversationService = Depends(get_conversation_service) ,security_manager: SecurityManager = Depends(get_security_manager)) -> List[dict]:
    # This is a protected router, so let's check for a token;
    await security_manager.verify_token(token)
    
    # Let's create the message and the respective conversation and store in the database;
    return await conversation_service.get_conversations(user_id)

@router.get('/{user_id}/{conversation_id}')
async def get_messages( conversation_id : int, message_service : MessageService = Depends(get_message_service) ,token: str = Depends(security), security_manager: SecurityManager = Depends(get_security_manager)):
    # This is a protected router, so let's check for a token;
    await security_manager.verify_token(token)

    # Let's create the message and the respective conversation and store in the database;
    return await message_service.get_messages(conversation_id)


@router.delete('/{user_id}/{conversation_id}')
async def delete_conversation( user_id : int, conversation_id : int,  token: str = Depends(security), conversation_service: ConversationService = Depends(get_conversation_service), security_manager: SecurityManager = Depends(get_security_manager)) -> str:
    # This is a protected router, so let's check for a token;
    await security_manager.verify_token(token)

    # Let's delete the conversation
    return await conversation_service.delete_conversation(conversation_id, user_id)
