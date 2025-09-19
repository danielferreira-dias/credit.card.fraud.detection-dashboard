from datetime import datetime
from app.infra.logger import setup_logger
from app.routers.auth_router import get_security_manager
from app.security.security import SecurityManager
from app.exception.user_exceptions import UserCredentialsException
from app.schemas.message_schema import ConversationCreate, ConversationResponse, MessageResponse
from app.settings.database import get_db
from app.service.message_service import ConversationService, MessageService
from app.repositories.message_repo import ConversationRepository, MessageRepository
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix = ['/messages'],
    tags ='messages'
)

logger = setup_logger(__name__)
security = HTTPBearer()

# --- Dependencies ---------------------------

def get_conversation_service(db: AsyncSession = Depends(get_db)):
    return ConversationService(db, get_conversation_repository(db))

def get_conversation_repository(db: AsyncSession = Depends(get_db)):
    return ConversationRepository(db)

def get_message_service(db: AsyncSession = Depends(get_db)):
    return MessageService(db, get_conversation_repository(db))

def get_message_repo(db: AsyncSession = Depends(get_db)):
    return MessageRepository(db, get_message_service(db))

# --- Router ---------------------------

@router.post('/{conversation_id}/message', response_model=MessageResponse)
async def send_message(role : str , conversation : ConversationCreate, conversation_service: ConversationService = Depends(get_conversation_service), message_service : MessageService = Depends(get_message_service) , token: str = Depends(security), security_manager: SecurityManager = Depends(get_security_manager)) -> ConversationResponse:

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

@router.get('/{user_id}')
async def get_messages( user_id : int,  token: str = Depends(security), security_manager: SecurityManager = Depends(get_security_manager)):
    # This is a protected router, so let's check for a token;
    payload = await security_manager.verify_token(token)
