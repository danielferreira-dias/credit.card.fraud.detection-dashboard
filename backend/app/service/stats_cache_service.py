from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.stats_cache_repo import StatsCacheRepository
from app.service.transaction_service import TransactionService
from app.schemas.filter_schema import TransactionFilter
from datetime import datetime, timedelta
from app.infra.logger import setup_logger

logger = setup_logger(__name__)

class StatsCacheService:
    # Cache TTL in minutes (adjust as needed)
    CACHE_TTL_MINUTES = 1000000
    STATS_OVERVIEW_KEY = "stats_overview"

    def __init__(self, db: AsyncSession):
        self.cache_repo = StatsCacheRepository(db)
        self.transaction_service = TransactionService(db)

    async def get_stats_overview(self, force_refresh: bool = False) -> dict:
        """
        Get stats overview from cache or compute and cache if stale/missing.

        Args:
            force_refresh: If True, bypass cache and recompute stats

        Returns:
            Dictionary with categorized stats
        """
        # Check cache unless force refresh
        if not force_refresh:
            cached = await self.cache_repo.get_cached_stats(self.STATS_OVERVIEW_KEY)

            if cached:
                # Check if cache is still valid
                cache_age = datetime.now() - cached.updated_at
                if cache_age < timedelta(minutes=self.CACHE_TTL_MINUTES):
                    logger.info(f"Returning cached stats (age: {cache_age})")
                    return cached.data
                else:
                    logger.info(f"Cache expired (age: {cache_age}), refreshing...")

        # Compute fresh stats
        logger.info("Computing fresh stats overview...")
        stats_data = await self._compute_stats_overview()

        # Cache the results
        await self.cache_repo.upsert_cached_stats(self.STATS_OVERVIEW_KEY, stats_data)

        return stats_data

    async def _compute_stats_overview(self) -> dict:
        """Compute stats overview (original logic from stats_router)."""
        # Step 1: Fetch all distinct values
        countries = await self.transaction_service.get_distinct_filter("country")
        merchant_categories = await self.transaction_service.get_distinct_filter("merchant_category")
        devices = await self.transaction_service.get_distinct_filter("device")
        channels = await self.transaction_service.get_distinct_filter("channel")
        distances = await self.transaction_service.get_distinct_filter("distance_from_home")

        high_risk_values = [True, False]
        weekend_values = [True, False]

        # Step 2: Create all filter objects
        all_filters = []
        filter_keys = []

        # Countries
        for country in countries:
            all_filters.append(TransactionFilter(country=country))
            filter_keys.append(("countries", country))

        # Merchant categories
        for cat in merchant_categories:
            all_filters.append(TransactionFilter(merchant_category=cat))
            filter_keys.append(("merchant_category", cat))

        # Devices
        for device in devices:
            all_filters.append(TransactionFilter(device=device))
            filter_keys.append(("device", device))

        # Channels
        for channel in channels:
            all_filters.append(TransactionFilter(channel=channel))
            filter_keys.append(("channel", channel))

        # High risk merchant
        for value in high_risk_values:
            all_filters.append(TransactionFilter(high_risk_merchant=value))
            filter_keys.append(("high_risk_merchant", value))

        # Distance from home
        for distance in distances:
            all_filters.append(TransactionFilter(distance_from_home=distance))
            filter_keys.append(("distance_from_home", distance))

        # Weekend transaction
        for value in weekend_values:
            all_filters.append(TransactionFilter(weekend_transaction=value))
            filter_keys.append(("weekend_transaction", value))

        # Step 3: Fetch all stats sequentially
        results = []
        for f in all_filters:
            result = await self.transaction_service.get_filtered_transactions_stats(f)
            results.append(result)

        # Step 4: Build categorized response
        response = {
            "countries": {},
            "merchant_category": {},
            "device": {},
            "channel": {},
            "high_risk_merchant": {},
            "distance_from_home": {},
            "weekend_transaction": {}
        }

        for (category, key), result in zip(filter_keys, results):
            response[category][key] = result

        return response

    async def refresh_cache(self) -> dict:
        """Force refresh the stats cache and return the new data."""
        return await self.get_stats_overview(force_refresh=True)
