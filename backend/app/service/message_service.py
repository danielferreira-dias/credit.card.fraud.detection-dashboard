
from datetime import datetime
from typing import List
from app.repositories.message_repo import ConversationRepository, MessageRepository
from app.schemas.message_schema import ConversationResponse, ConversationCreate, MessageCreate, MessageResponse
from app.models.user_model import Conversation, Message
from app.exception.chat_exceptions import ChatNotFound
from app.service.user_service import UserService
from app.infra.logger import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.misc.metada_info import initial_metadata

logger = setup_logger(__name__)

class ConversationService():
    def __init__(self, repo: ConversationRepository, message_repo: MessageRepository, user_service : UserService):
        self.repo = repo
        self.message_repo = message_repo
        self.user_service = user_service

    async def create_conversation(self, conversation: ConversationCreate) -> int:
        conversation_model = Conversation(
            user_id = conversation.user_id,
            title = conversation.title,
            thread_id =  conversation.thread_id,
            created_at = conversation.created_at,
            updated_at = conversation.created_at,
            is_active = True,
            total_messages = 1,
            metadata_info = conversation.metadata_info,
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

    async def get_conversations(self, user_id: int) -> List[dict]:
        # Verify user exists
        await self.user_service.get_user_service(user_id)

        # Get all conversations for the user
        conversations = await self.repo.get_conversations_by_user_id(user_id)

        # Convert to response format
        return [{"id": conv.id, "title": conv.title, "thread_id": conv.thread_id, "updated_at": conv.updated_at} for conv in conversations]
    
    async def get_conversation_by_conversation_id(self, conversation_id : int ) -> Conversation:
        # Get all conversations for the user
        return await self.repo.get_conversation(conversation_id)

    async def delete_conversation(self, conversation_id: int, user_id: int) -> str:
        # Verify user exists
        await self.user_service.get_user_service(user_id)

        # Verify conversation exists and belongs to user
        conversation = await self.repo.get_conversation(conversation_id)
        if conversation is None:
            raise ChatNotFound(f"Conversation with id {conversation_id} not found")

        if conversation.user_id != user_id:
            raise ChatNotFound("Conversation does not belong to this user")

        # Store thread_id before deleting conversation
        thread_id = conversation.thread_id

        # Delete all messages first
        await self.message_repo.delete_conversation_messages(conversation_id)

        # Delete LangGraph checkpoints associated with this thread
        if thread_id:
            await self.repo.delete_checkpoints_by_thread_id(thread_id)

        # Delete the conversation
        await self.repo.delete_conversation(conversation_id)

        return f"Conversation {conversation_id}, its messages, and checkpoints have been deleted"

    async def update_last_activity(self, conversation_id: int):
        await self.repo.update_conversation(conversation_id)

    @classmethod
    def _to_response(cls, conv: Conversation, user_role: str, message: str) -> ConversationResponse:
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
            role = user_role,
            content = message,
            created_at = conv.created_at
        )
        
class MessageService():
    def __init__(self, db: AsyncSession, repo: MessageRepository, conversation_repo: ConversationRepository):
        self.repo = repo
        self.conversation_repo = conversation_repo

    async def create_message(self, conversation_id : int , message: MessageCreate) -> MessageResponse:
        # Verify conversation exists
        conversation = await self.conversation_repo.get_conversation(conversation_id)
        if conversation is None:
            raise ChatNotFound(f"Conversation with id {conversation_id} not found")
        new_message = Message(
            conversation_id=conversation_id,
            role=message.role,
            content=message.message,
            created_at=datetime.now(),
            reasoning_steps=message.reasoning_steps
        )
        return await self.repo.create_message(conversation_id, new_message)

    async def get_messages(self, conversation_id: int) -> List[ConversationResponse]:
        # Verify conversation exists
        conversation = await self.conversation_repo.get_conversation(conversation_id)

        if conversation is None:
            raise ChatNotFound(f"Conversation with id {conversation_id} not found")

        # Get all messages for the conversation
        messages = await self.repo.get_messages_by_conversation_id(conversation_id)

        # Convert to response format
        return [ConversationResponse(
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            reasoning_steps=msg.reasoning_steps
        ) for msg in messages]

async def websocket_conversation_handle(conversation_service: ConversationService, thread_id : str ,current_conversation_id : int | None, user_id : int, title: str | None ) -> tuple[int, str]:
    # Handle conversation initialization
    if not current_conversation_id:
        # Create new conversation with generated thread_id
        
        current_conversation_id = await conversation_service.create_conversation(ConversationCreate(
            user_id=user_id,
            title=title,  # This will be generated by a NLP
            thread_id=thread_id,
            created_at=datetime.now(),
            metadata_info=initial_metadata
        ))

        return current_conversation_id, thread_id
    else:
        # Retrieve existing conversation to get thread_id
        conversation : Conversation = await conversation_service.get_conversation_by_conversation_id(current_conversation_id)
        thread_id : str = conversation.thread_id if conversation else f"user_{user_id}_{current_conversation_id}"
        return current_conversation_id, thread_id  # Fixed: return thread_id, not conversation.id