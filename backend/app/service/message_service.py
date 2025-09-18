
from app.repositories.message_repo import ConversationRepository, MessageRepository
from app.schemas.message_schema import ConversationResponse, MessageCreate, MessageResponse
from sqlalchemy.ext.asyncio import AsyncSession

class ConversationService():
    def __init__(self, db: AsyncSession):
        self.repo = ConversationRepository(db)

    async def create_conversation(self, message: MessageCreate) -> ConversationResponse:
        self.repo.create_conversation(message)

class MessageService():
    def __init__(self, db: AsyncSession):
        self.repo = MessageRepository(db)

    async def create_message(self, conversation_id : int ,message: str) -> MessageResponse:
        self.repo.add_message(conversation_id, message)

