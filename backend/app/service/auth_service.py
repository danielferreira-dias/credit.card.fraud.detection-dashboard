from app.security.security import SecurityManager
from app.service.user_service import UserService
from app.exception.user_exceptions import UserCredentialInvalid
from app.schemas.user_schema import UserAuthenticationReponse
from app.infra.logger import setup_logger
from app.schemas.auth_schema import Token, TokenResponse

logger = setup_logger(__name__)



class AuthService:
    def __init__(self, security_manager : SecurityManager, user_service: UserService):
        self.security = security_manager
        self.user_service = user_service
    
    async def login_service(self, email: str, password: str) -> TokenResponse:
        if email is None or email == "":
            raise UserCredentialInvalid('Invalid Email')
        if password is None or email == "":
            raise UserCredentialInvalid('Invalid Password')
        user_data : UserAuthenticationReponse = await self.security.authenticate_user(email, password) 

        if not user_data:
            raise UserCredentialInvalid('Invalid Credentials by the User')
        
        access_token = self.security.create_access_token(user_data.model_dump())
        return TokenResponse( user_email=user_data.email , token=Token(access_token=access_token, token_type="bearer"))