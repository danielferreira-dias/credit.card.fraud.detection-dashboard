from app.security.security import SecurityManager
from app.service.user_service import UserService
from app.exception.user_exceptions import UserCredentialInvalid
from app.schemas.user_schema import UserAuthenticationReponse, UserRegisterSchema
from app.infra.logger import setup_logger
from app.schemas.auth_schema import Token, TokenResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from fastapi import HTTPException
import os
from dotenv import load_dotenv

logger = setup_logger(__name__)

load_dotenv()

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
        return TokenResponse( user_email=user_data.email, name = user_data.name , token=Token(access_token=access_token, token_type="bearer"))

    async def google_auth_service(self, google_token: str) -> TokenResponse:
        """
        Verify Google OAuth token and authenticate/register user
        """
        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(
                google_token,
                requests.Request(),
                os.getenv("GOOGLE_CLIENT_ID")  # You should add your Google Client ID here from environment
            )

            # Extract user information from Google token
            email = idinfo.get('email')
            name = idinfo.get('name', email)

            if not email:
                raise HTTPException(status_code=400, detail="Email not found in Google token")

            logger.info(f"Google authentication for email: {email}")

            user_create_data = UserRegisterSchema(
                email=email,
                name=name,
                password="oauth_google_user",  # Placeholder password for OAuth users
                confirm_password="oauth_google_user"
            )

            # Check if user already exists
            try:
                await self.user_service.create_user_service(user_create_data)
            except UserCredentialInvalid:
                # User already exists, proceed to login
                pass

            # Create access token for our app
            user_data = UserAuthenticationReponse(email=email, name=name)
            access_token = self.security.create_access_token(user_data.model_dump())

            return TokenResponse(
                user_email=email,
                name=name,
                token=Token(access_token=access_token, token_type="bearer")
            )

        except ValueError as e:
            logger.error(f"Invalid Google token: {e}")
            raise HTTPException(status_code=401, detail="Invalid Google token")
        except Exception as e:
            logger.error(f"Google authentication error: {e}")
            raise HTTPException(status_code=500, detail="Google authentication failed")