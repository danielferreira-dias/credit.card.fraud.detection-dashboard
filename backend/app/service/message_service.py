
from typing import List
from app.repositories.message_repo import ConversationRepository, MessageRepository
from app.schemas.message_schema import ConversationResponse, ConversationCreate, MessageResponse
from app.models.user_model import Conversation
from app.exception.chat_exceptions import ChatException, ChatNotFound
from app.service.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class ConversationService():
    def __init__( self, db: AsyncSession, repo: ConversationRepository, user_service : UserService) :
        self.repo = repo(db)
        self.user_service = user_service

    async def create_conversation(self, conversation: ConversationCreate) -> int:
        conversation_model = Conversation(
            user_id = conversation.user_id,
            title = conversation.title or "New Chat",
            created_at = conversation.created_at
        )
        return await self.repo.create_conversation(conversation_model)

    async def add_message_to_conversation(self, conversation_updated: ConversationCreate, conversation_id : int) -> str:
        current_conversation : Conversation = await self.repo.get_conversation(conversation_id)
        if current_conversation is None:
            raise ChatNotFound("Chat Conversation has not been found;")
        
        for key, value in conversation_updated.__dict__.items():
            if key != "transaction_id" and value is not None:
                setattr(conversation_updated, key, value)

        updated_conversation = await self.repo.add_conversation_message(conversation_id)
        return f'Conversation {updated_conversation.id} was updated'

    async def get_conversations(self, user_id: int) -> List[str]:
        # Verify user exists
        await self.user_service.get_user_service(user_id)

        # Get all conversations for the user
        conversations = await self.repo.get_conversations_by_user_id(user_id)

        # Convert to response format
        return [conv.title for conv in conversations]

    @classmethod
    def _to_response(cls, conv: Conversation, user_name: str, user_role: str, message: str) -> ConversationResponse:
        """
        Converts a Transaction model instance to a TransactionResponse schema.
        Args:
            ts (Transaction): The transaction model instance.
        Returns:
            TransactionResponse: The transaction response schema.
        """
        if conv is None:
            raise ValueError("Transaction instance cannot be None")

        return ConversationResponse(
            name = user_name,
            role = user_role,
            content = message,
            created_at = conv.created_at
        )
        

class MessageService():
    def __init__(self, db: AsyncSession, repo: MessageRepository, conversation_repo: ConversationRepository):
        self.repo = repo(db)
        self.conversation_repo = conversation_repo(db)

    async def create_message(self, conversation_id : int , message: ConversationCreate) -> MessageResponse:
        # Verify conversation exists
        conversation = await self.conversation_repo.get_conversation(conversation_id)
        if conversation is None:
            raise ChatNotFound(f"Conversation with id {conversation_id} not found")
        return await self.repo.create_message(conversation_id, message.content)

