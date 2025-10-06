from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.settings.database import get_db
from app.service.transaction_service import TransactionService
from app.service.stats_cache_service import StatsCacheService
from app.infra.logger import setup_logger
from app.schemas.filter_schema import TransactionFilter
import asyncio

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

logger = setup_logger(__name__)

def get_transaction_service(db: AsyncSession = Depends(get_db)) -> TransactionService:
    """ Dependency to get the TransactionService with a database session. """
    return TransactionService(db)

def get_stats_cache_service(db: AsyncSession = Depends(get_db)) -> StatsCacheService:
    """ Dependency to get the StatsCacheService with a database session. """
    return StatsCacheService(db)

# ------------------------------------------ Routers

@router.get('/countries')
async def get_stats_countries( transaction_service : TransactionService = Depends(get_transaction_service)):
    countries = await transaction_service.get_distinct_filter("country")

    # Create all filter objects
    filters = [TransactionFilter(country=country) for country in countries]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        country: result 
        for country, result in zip(countries, results)
    }

    return response

@router.get('/merchant_category')
async def get_stats_merchant_category( transaction_service : TransactionService = Depends(get_transaction_service)):
    merchant_category = await transaction_service.get_distinct_filter("merchant_category")

    # Create all filter objects
    filters = [TransactionFilter(merchant_category==merchant_cat) for merchant_cat in merchant_category]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        merchant_cat: result 
        for merchant_cat, result in zip(merchant_category, results)
    }

    return response

@router.get('/device')
async def get_stats_device( transaction_service : TransactionService = Depends(get_transaction_service)):
    devices = await transaction_service.get_distinct_filter("device")

    # Create all filter objects
    filters = [TransactionFilter(device==device) for device in devices]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        device: result 
        for device, result in zip(devices, results)
    }

    return response

@router.get('/channel')
async def get_stats_channel( transaction_service : TransactionService = Depends(get_transaction_service)):
    channels = await transaction_service.get_distinct_filter("device")

    # Create all filter objects
    filters = [TransactionFilter(channel==channel) for channel in channels]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        channel: result 
        for channel, result in zip(channels, results)
    }

    return response

@router.get('/high_risk_merchant')
async def get_stats_high_risk_merchant( transaction_service : TransactionService = Depends(get_transaction_service)):
    high_risk_merchants = [True, False]

    # Create all filter objects
    filters = [TransactionFilter(high_risk_merchant==high_risk_merchant) for high_risk_merchant in high_risk_merchants]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        high_risk_merchant: result 
        for high_risk_merchant, result in zip(high_risk_merchants, results)
    }

    return response

@router.get('/distance_from_home')
async def get_stats_distance_from_home( transaction_service : TransactionService = Depends(get_transaction_service)):
     # Boolean field: True and False
    distances = [1, 0]

    # Create all filter objects
    filters = [TransactionFilter(distance_from_home=distance) for distance in distances]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        distance: result
        for distance, result in zip(distances, results)
    }

    return response

@router.get('/weekend_transaction')
async def get_stats_weekend_transaction( transaction_service : TransactionService = Depends(get_transaction_service)):
    # Boolean field: True and False
    weekend_values = [True, False]

    # Create all filter objects
    filters = [TransactionFilter(weekend_transaction=value) for value in weekend_values]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        value: result
        for value, result in zip(weekend_values, results)
    }

    return response

@router.get('/overview')
async def get_stats_overview( force_refresh: bool = Query(False, description="Force refresh the cache"), stats_cache_service: StatsCacheService = Depends(get_stats_cache_service)):
    """
        Get stats overview. Returns cached data if available and not stale.
        Use force_refresh=true to bypass cache and recompute.
    """
    return await stats_cache_service.get_stats_overview(force_refresh=force_refresh)

@router.post('/refresh-cache')
async def refresh_stats_cache(stats_cache_service: StatsCacheService = Depends(get_stats_cache_service)):
    """
    Manually refresh the stats cache. Useful for triggering updates after data imports.
    """
    result = await stats_cache_service.refresh_cache()
    return {
        "status": "success",
        "message": "Stats cache refreshed successfully",
        "data": result
    }
