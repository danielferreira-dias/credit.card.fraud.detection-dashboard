from app.security.security import SecurityManager
from app.service.user_service import UserService
from app.exception.user_exceptions import UserCredentialInvalid
from app.schemas.user_schema import UserAuthenticationReponse
from dataclasses import dataclass
from app.infra.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class Token:
    access_token: str
    token_type: str

class AuthService:
    def __init__(self, security_manager : SecurityManager, user_service: UserService):
        self.security = security_manager
        self.user_service = user_service
    
    async def login_service(self, email: str, password: str) -> Token:
        logger.info(f"Current info ->  {email}, + {password}")
        user_data : UserAuthenticationReponse = await self.security.authenticate_user(email, password) 
        logger.info(f"user_data -> {user_data}")

        if not user_data:
            raise UserCredentialInvalid('Invalid Credentials by the User')
        
        access_token = self.security.create_access_token(user_data.model_dump())
        return Token(access_token=access_token, token_type="bearer")