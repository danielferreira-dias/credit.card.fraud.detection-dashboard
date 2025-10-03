from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class ConversationCreate(BaseModel):
    user_id: int
    title: Optional[str] = None
    thread_id: Optional[str] = None
    created_at: datetime = datetime.now()
    metadata_info: Optional[dict] = None

class MessageCreate(BaseModel):
    role: str
    message: str
    reasoning_steps: Optional[list[dict]] = None

class ConversationListResponse(BaseModel):
    id: int
    title: str
    thread_id: str
    updated_at: Optional[datetime]

class ConversationsListResponse(BaseModel):
    conversations: list[ConversationListResponse]

class MessageResponse(BaseModel):
    email: EmailStr
    name: str 

class ConversationResponse(BaseModel):
    role: str
    content: str
    created_at: datetime = datetime.now()
    reasoning_steps: Optional[list[dict]] = None