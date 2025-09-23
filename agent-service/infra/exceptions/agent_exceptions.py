from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

class AgentException(Exception):
    def __init__(self, name: str = "Agent Exception", message: str = "An Agent Exception was raised."):
        self.name = name
        self.message = message
        super().__init__(self.message, self.name)
    
    def to_http_status(self):
        return HTTP_500_INTERNAL_SERVER_ERROR