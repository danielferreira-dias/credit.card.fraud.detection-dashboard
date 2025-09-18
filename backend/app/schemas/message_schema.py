from datetime import datetime
from pydantic import BaseModel, EmailStr


class MessageCreate(BaseModel):
    user_id: int 
    title : str
    content: str
    sent_at: datetime

class MessageResponse(BaseModel):
    email: EmailStr
    name: str 

class ConversationResponse(BaseModel):
    email: EmailStr
    name: str 
    role: str
    content: str
    created_at: datetime