from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

class TransactionsException(Exception):
    def __init__(self, name: str = "Service is unavailable", message: str = "Transaction API Exception"):
        self.name = name
        self.message = message
        super().__init__(self.message, self.name)

class EntityNotFoundException(TransactionsException):
    """Exception raised when an entity is not found in the database."""
    pass

class DatabaseException(TransactionsException):
    """Exception raised for database-related errors."""
    pass

class InvalidTransactionDataException(TransactionsException):
    """Exception raised when transaction data is invalid."""
    pass

class PredictionException(TransactionsException):
    """Exception raised when there is an error during prediction."""
    pass

