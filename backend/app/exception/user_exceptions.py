from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT, HTTP_401_UNAUTHORIZED

class UserException(Exception):
    """Base class for user-related exceptions."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR

class UserNotFoundException(UserException):
    """Exception raised when a user is not found."""
    def to_http_status(self):
        return HTTP_404_NOT_FOUND

class UserCredentialInvalid(UserException):
    """Exception raised when invalid credentials"""
    def to_http_status(self):
        return HTTP_401_UNAUTHORIZED
    
class UserCredentialsException(UserException):
    def to_http_status(self):
        return HTTP_401_UNAUTHORIZED
    
class UserDuplicateException(UserException):
    def to_http_status(self):
        return HTTP_400_BAD_REQUEST