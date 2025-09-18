from app.models.user_model import Conversation, Message
from sqlalchemy import select, func
from app.schemas.message_schema import MessageCreate
from sqlalchemy.ext.asyncio import AsyncSession

class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(self, message: MessageCreate ) -> Conversation:
        pass

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_message(self, message: str) -> Message:
        pass
    
    

