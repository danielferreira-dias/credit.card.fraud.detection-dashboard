
# app/exception/handler.py

from app.exception.user_exceptions import UserException
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exception.transaction_exceptions import TransactionsException
import logging

logger = logging.getLogger(__name__)

async def transaction_handler(request: Request, exc: TransactionsException):
    logger.error(f"{exc.__class__.__name__}: {exc.message}")
    return JSONResponse(
        status_code=exc.to_http_status(),
        content={"message": exc.message}
    )

async def user_handler(request: Request, exc: UserException):
    logger.error(f"{exc.__class__.__name__}: {exc.message}")
    return JSONResponse(
        status_code=exc.to_http_status(),
        content={"message": exc.message}
    )