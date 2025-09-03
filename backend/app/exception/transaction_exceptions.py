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

# Convert exception to appropriate HTTP status code

class EntityError(TransactionsException):
    """Exception raised when a requested entity is not found."""

    def __init__(self, name: str = "Entity Not Found", message: str = "The requested entity was not found"):
        self.detail = f"{name}: {message}"
        super().__init__(self.detail)

    def to_http_status(self):
        return HTTP_404_NOT_FOUND
    

class DatabaseException(TransactionsException):
    """Exception raised for database-related errors."""

    def __init__(self, name: str = "Internal Error", message: str = "Database operation failed"):
        self.message = message
        self.name = name
        super().__init__(name=self.default_name, message=message)
    
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR

class DuplicateTransactionError(TransactionsException):
    """Exception raised for duplicated keys"""

    def __init__(self, name: str = "Duplicate Transaction", message: str = "A transaction with this ID already exists"):
        self.name = name
        self.message = message
        super().__init__(self.name, self.message)
    
    def to_http_status(self):
        return HTTP_409_CONFLICT

class InvalidDataError(TransactionsException):
    """Exception raised when transaction data is invalid."""

    def __init__(self, name: str = "Invalid Transaction Data", message: str = "The provided transaction data is invalid"):
        self.detail = f"{name}: {message}"
        super().__init__(self.detail)
    
    def to_http_status(self):
        return HTTP_400_BAD_REQUEST

class PredictionError(TransactionsException):
    """Exception raised when there is an error during prediction."""

    def __init__(self, name: str = "Prediction Error", message: str = "An error occurred during the prediction process"):
        self.detail = f"{name}: {message}"
        super().__init__(self.detail)
    
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR

class ModelNotLoadedError(TransactionsException):
    """Exception raised when the ML model is not loaded properly."""

    def __init__(self, name: str = "Model Not Loaded", message: str = "The machine learning model is not loaded"):
        self.name = name
        self.message = message
        super().__init__(name=self.name, message=self.message)

class ScalerNotLoadedError(TransactionsException):
    """Exception raised when the scaler is not loaded properly."""

    def __init__(self, name: str = "Scaler Not Loaded", message: str = "The scaler for feature transformation is not loaded"):
        self.name = name
        self.message = message
        super().__init__(name=self.name, message=self.message)

class PipelineNotLoadedError(TransactionsException):
    """Exception raised when the ML pipeline is not loaded properly."""

    def __init__(self, name: str = "Pipeline Not Loaded", message: str = "The machine learning pipeline is not loaded"):
        self.name = name
        self.message = message
        super().__init__(name=self.name, message=self.message)
