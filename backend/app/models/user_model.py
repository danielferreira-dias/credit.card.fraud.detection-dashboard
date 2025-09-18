from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.settings.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    confirmed = Column(Boolean, nullable=False)

    conversations = relationship("Conversation", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.name}, email={self.email})>"

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    conversation = relationship("Conversation", back_populates="messages")
