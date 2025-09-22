from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT

class ChatException(Exception):
    """Base exception class for Message/Conversation Service related errors."""
    def __init__(self, name: str = "Service is unavailable", message: str = "Conversation API Exception"):
        self.name = name
        self.message = message
        super().__init__(self.message, self.name)
    
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR
    

class ChatNotFound(ChatException):
    def __init__(self, name: str = "Service is unavailable", message: str = "Conversation API Exception"):
        self.name = name
        self.message = message
        super().__init__(self.message, self.name)
    
    def to_http_status(self):
        return HTTP_404_NOT_FOUND