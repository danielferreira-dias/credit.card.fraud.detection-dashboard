from datetime import datetime
from app.infra.logger import setup_logger
from app.routers.auth_router import get_security_manager
from app.security.security import SecurityManager
from app.exception.user_exceptions import UserCredentialsException
from app.schemas.message_schema import MessageCreate, MessageResponse
from app.settings.database import get_db
from app.service.message_service import ConversationService, MessageService
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

def get_message_service(db: AsyncSession = Depends(get_db)):
    return MessageService(db)

def get_conversation_service(db: AsyncSession = Depends(get_db)):
    return ConversationService(db)

# --- Router ---------------------------
@router.post('/{conversation_id}/message', response_model=MessageResponse)
async def send_message(message : MessageCreate, conversation_service: ConversationService = Depends(get_conversation_service), message_service : MessageService = Depends(get_message_service) ,token: str = Depends(security), security_manager: SecurityManager = Depends(get_security_manager)) -> MessageResponse:

    # This is a protected router, so let's check for a token;
    payload = await security_manager.verify_token(token)

    # Check if there's an existing token;
    if payload is None:
        raise UserCredentialsException('Invalid token')
    
    # Let's create the message and store in the database;
    ## Should it be Async here? What if we need to create a conversation and get its ID;
    await conversation_service.create_conversation(message)
    await message_service.create_message(message.content)

    return MessageResponse(
        email = payload['user'].get('email'),
        name = payload['user'].get('name'),
        role = 'User',
        content = message,
        created_at = datetime.now()
    )
