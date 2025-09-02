
# app/exception/handler.py

from fastapi import Request
from fastapi.responses import JSONResponse
from app.exception.transaction_exceptions import TrasanctionsException
import logging

logger = logging.getLogger(__name__)

async def transaction_service_exception_handler(request: Request, exc: TrasanctionsException):
    logger.error(f"{exc.__class__.__name__}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )