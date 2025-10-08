from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.settings.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    confirmed = Column(Boolean, nullable=False)

    conversations = relationship("Conversation", back_populates="user")
    reports = relationship("Report", back_populates="user")
    analysis = relationship("Analysis", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.name}, email={self.email})>"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), nullable=False, index=True)  # Changed to String for LangGraph compatibility
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # Auto-update on changes
    is_active = Column(Boolean, default=True)  
    total_messages = Column(Integer, default=0) 
    metadata_info = Column(JSON)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    reasoning_steps = Column(JSON, nullable=True)  # Store agent reasoning steps as JSON array

    conversation = relationship("Conversation", back_populates="messages")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    report_content = Column(JSON, nullable=True)  
    user = relationship("User", back_populates="reports")

class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    analysis_content = Column(JSON, nullable=True)  

    user = relationship("User", back_populates="analysis")
    transaction = relationship("Transaction", back_populates="analysis")
