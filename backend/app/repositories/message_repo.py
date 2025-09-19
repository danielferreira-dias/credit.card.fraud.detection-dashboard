from typing import List
from app.models.user_model import Conversation, Message
from app.infra.logger import setup_logger
from app.exception.chat_exceptions import ChatException, ChatNotFound
from sqlalchemy import select, func
from app.schemas.message_schema import ConversationCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

logger = setup_logger(__name__)

class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_conversation(self, conversation_id: int) -> Conversation:
        try:
            result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter user com ID {conversation_id}: {e}")
            raise ChatException("Error in the Conversation Database;") from e
    
    async def get_conversations_by_user_id(self, user_id: int) -> List[Conversation]:
        try:
            result = await self.db.execute(select(Conversation).where(Conversation.user_id == user_id))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao obter conversas do user com ID {user_id}: {e}")
            raise ChatException("Error in the Conversation Database;") from e
    
    async def create_conversation(self, conversation: Conversation) -> int:
        try:
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation) # ← This fetches the latest data
            return conversation.id
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar uma nova conversa; {e}")
            raise ChatException("Error in the Conversation Database;") from e
    
    async def add_conversation_message(self, updated_conversation : Conversation ) -> Conversation:
        try:
            await self.db.commit()
            await self.db.refresh(updated_conversation)
            return updated_conversation
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao atualizar transação: {e}")
            raise ChatException("Error in the Conversation Database;") from e

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_message(self, conversation_id: int , message: Message) -> Message:
        try:
            message.conversation_id = conversation_id
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message) # ← This fetches the latest data
            return message
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Erro ao atualizar transação: {e}")
            raise ChatException("Error in the Messages Database;") from e
    
    

