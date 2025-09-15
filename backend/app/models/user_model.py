from sqlalchemy import Column, Integer, Float, Boolean, DateTime, String
from app.settings.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"