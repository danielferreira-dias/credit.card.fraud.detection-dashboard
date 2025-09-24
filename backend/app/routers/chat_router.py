from datetime import datetime
from typing import List
import json
import aiohttp
import os
from app.infra.logger import setup_logger
from app.routers.auth_router import get_security_manager, get_user_service
from app.security.security import SecurityManager
from app.exception.user_exceptions import UserCredentialsException
from app.schemas.message_schema import ConversationCreate, ConversationResponse, MessageResponse
from app.settings.database import get_db
from app.service.message_service import ConversationService, MessageService
from app.repositories.message_repo import ConversationRepository, MessageRepository
from app.ws.connection_manager import ConnectionManager
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
    return ConversationService(db, get_conversation_repository(db), get_message_repo(db), get_user_service(db))

def get_conversation_repository(db: AsyncSession = Depends(get_db)):
    return ConversationRepository(db)


def get_connection_manager():
    return ConnectionManager()

# Agent service configuration
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8001")

async def query_agent_service(user_message: str) -> str:
    """Query the agent service and return the response"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"query": user_message}
            async with session.post(
                f"{AGENT_SERVICE_URL}/user_message",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.text()
                    # Remove quotes if the response is a JSON string
                    if result.startswith('"') and result.endswith('"'):
                        result = result[1:-1].replace('\\"', '"')
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Agent service error {response.status}: {error_text}")
                    return f"Agent service error: {response.status}"
    except aiohttp.ClientError as e:
        logger.error(f"Failed to connect to agent service: {str(e)}")
        return "Failed to connect to agent service. Please check if the service is running."
    except Exception as e:
        logger.error(f"Unexpected error querying agent service: {str(e)}")
        return f"Unexpected error: {str(e)}"

# --- Router ---------------------------


@router.websocket("/ws/agent/{client_id}")
async def agent_websocket_endpoint(websocket: WebSocket, client_id: int, connection_manager: ConnectionManager = Depends(get_connection_manager)):
    """WebSocket endpoint for chat with AI agent"""
    await connection_manager.connect(websocket)
    logger.info(f"Agent chat connected for client {client_id}")

    try:
        # Send welcome message
        welcome_message = {
            "type": "system",
            "content": "Connected to AI Agent. Ask me about transactions, fraud detection, or any analysis!",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_message))

        while True:
            # Receive user message
            user_input = await websocket.receive_text()
            logger.info(f"Received message from client {client_id}: {user_input}")

            try:
                # Parse JSON if it's structured data
                message_data = json.loads(user_input)
                user_message = message_data.get("content", user_input)
            except json.JSONDecodeError:
                # Plain text message
                user_message = user_input

            # Echo user message back
            user_echo = {
                "type": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(user_echo))

            # Send typing indicator
            typing_indicator = {
                "type": "typing",
                "content": "Agent is thinking...",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(typing_indicator))

            # Query the agent service
            agent_response = await query_agent_service(user_message)

            # Send agent response
            agent_message = {
                "type": "agent",
                "content": agent_response,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(agent_message))

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info(f"Agent chat disconnected for client {client_id}")

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
