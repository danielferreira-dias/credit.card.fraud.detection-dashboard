from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.settings.database import get_db
from app.service.transaction_service import TransactionService
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

@router.get('/card_present')
async def get_stats_card_present( transaction_service : TransactionService = Depends(get_transaction_service)):
    # Boolean field: True and False
    card_present_values = [True, False]

    # Create all filter objects
    filters = [TransactionFilter(card_present=value) for value in card_present_values]

    # Fetch all concurrently
    results = await asyncio.gather(
        *[transaction_service.get_filtered_transactions_stats(f) for f in filters]
    )

    # Build response
    response = {
        value: result
        for value, result in zip(card_present_values, results)
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
async def get_stats_overview(transaction_service: TransactionService = Depends(get_transaction_service)):
    # Step 1: Fetch all distinct values first (sequentially to avoid session conflicts)
    countries = await transaction_service.get_distinct_filter("country")
    merchant_categories = await transaction_service.get_distinct_filter("merchant_category")
    devices = await transaction_service.get_distinct_filter("device")
    channels = await transaction_service.get_distinct_filter("channel")
    distances = await transaction_service.get_distinct_filter("distance_from_home")

    high_risk_values = [True, False]
    card_present_values = [True, False]
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

    # Card present
    for value in card_present_values:
        all_filters.append(TransactionFilter(card_present=value))
        filter_keys.append(("card_present", value))

    # Weekend transaction
    for value in weekend_values:
        all_filters.append(TransactionFilter(weekend_transaction=value))
        filter_keys.append(("weekend_transaction", value))

    # Step 3: Fetch all stats sequentially (to avoid DB session conflicts)
    results = []
    for f in all_filters:
        result = await transaction_service.get_filtered_transactions_stats(f)
        results.append(result)

    # Step 4: Build categorized response
    response = {
        "countries": {},
        "merchant_category": {},
        "device": {},
        "channel": {},
        "high_risk_merchant": {},
        "distance_from_home": {},
        "card_present": {},
        "weekend_transaction": {}
    }

    for (category, key), result in zip(filter_keys, results):
        response[category][key] = result

    return response
