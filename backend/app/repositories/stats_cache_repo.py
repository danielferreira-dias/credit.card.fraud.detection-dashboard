from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.stats_cache_model import StatsCache
from typing import Optional
from app.infra.logger import setup_logger
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

logger = setup_logger(__name__)

class StatsCacheRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cached_stats(self, cache_key: str) -> Optional[StatsCache]:
        """Retrieve cached stats by key."""
        try:
            stmt = select(StatsCache).where(StatsCache.cache_key == cache_key)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching cached stats for key '{cache_key}': {e}")
            return None

    async def upsert_cached_stats(self, cache_key: str, data: dict) -> StatsCache:
        """Insert or update cached stats."""
        try:
            # Try to get existing cache entry within the same transaction
            stmt = select(StatsCache).where(StatsCache.cache_key == cache_key)
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing entry
                existing.data = data
                existing.updated_at = datetime.utcnow()
                await self.db.commit()
                await self.db.refresh(existing)
                logger.info(f"Updated cache for key '{cache_key}'")
                return existing
            else:
                # Create new entry
                new_cache = StatsCache(
                    cache_key=cache_key,
                    data=data
                )
                self.db.add(new_cache)
                await self.db.commit()
                await self.db.refresh(new_cache)
                logger.info(f"Created new cache for key '{cache_key}'")
                return new_cache
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error upserting cached stats for key '{cache_key}': {e}")
            raise

    async def delete_cached_stats(self, cache_key: str) -> bool:
        """Delete cached stats by key."""
        try:
            existing = await self.get_cached_stats(cache_key)
            if existing:
                await self.db.delete(existing)
                await self.db.commit()
                logger.info(f"Deleted cache for key '{cache_key}'")
                return True
            return False
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting cached stats for key '{cache_key}': {e}")
            raise
