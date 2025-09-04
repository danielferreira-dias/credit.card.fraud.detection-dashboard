from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT

class TransactionsException(Exception):
    """Base exception class for transaction service related errors."""
    def __init__(self, name: str = "Service is unavailable", message: str = "Transaction API Exception"):
        self.name = name
        self.message = message
        super().__init__(self.message, self.name)
    
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR

# Database related exceptions -------------------------

class DatabaseException(TransactionsException):
    """Exception raised for database related errors."""
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR

class TransactionNotFoundError(TransactionsException):
    """Exception raised when a transaction is not found."""
    def to_http_status(self):
        return HTTP_404_NOT_FOUND

class TransactionCreationError(TransactionsException):
    """Exception raised when there is an error creating a transaction."""
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR
    
class TransactionDuplucateError(TransactionsException):
    """Exception raised when a duplicate transaction is detected."""
    def to_http_status(self):
        return HTTP_409_CONFLICT

class TransactionInvalidDataError(TransactionsException):
    """Exception raised when invalid data is provided for a transaction."""
    def to_http_status(self):
        return HTTP_400_BAD_REQUEST

# Model related exceptions ----------------------------

class ModelNotLoadedError(TransactionsException):
    """Exception raised when the ML model is not loaded properly."""
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR

class ScalerNotLoadedError(TransactionsException):
    """Exception raised when the scaler is not loaded properly."""
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR

class PipelineNotLoadedError(TransactionsException):
    """Exception raised when the ML pipeline is not loaded properly."""
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR
