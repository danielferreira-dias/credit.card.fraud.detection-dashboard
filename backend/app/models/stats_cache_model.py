from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime
from app.settings.base import Base

class StatsCache(Base):
    __tablename__ = 'stats_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String, unique=True, nullable=False, index=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def __repr__(self):
        return f"<StatsCache(cache_key='{self.cache_key}', updated_at='{self.updated_at}')>"
