from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class ConversationCreate(BaseModel):
    user_id: int 
    conversation_id: Optional[int] = None
    conversation_title: Optional[str] = None
    content: str
    created_at: datetime

class ConversationListResponse(BaseModel):
    conversation_id: Optional[int] = None
    conversation_title: Optional[str] = None

class MessageResponse(BaseModel):
    email: EmailStr
    name: str 


class ConversationResponse(BaseModel):
    role: str
    content: str
    created_at: datetime