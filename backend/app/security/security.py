from datetime import datetime, timedelta, timezone
import os
from app.service.user_service import UserService
import jwt
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from app.exception.user_exceptions import UserCredentialInvalid, UserCredentialsException, UserException, UserNotFoundException
from app.schemas.user_schema import UserAuthenticationReponse, UserResponse, UserSchema
from jwt.exceptions import InvalidTokenError
from .password_utils import verify_password, hash_password

load_dotenv()

class SecurityManager:
    def __init__(self, user_service: UserService):
        self.secret_key = os.getenv("SECRET_KEY")
        if self.secret_key is None:
            raise UserException('Secret Key is not set;')
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.user_service = user_service

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    async def authenticate_user(self, user_email : EmailStr, password: str) -> UserAuthenticationReponse:
        try:
            user : UserSchema = await self.user_service.get_user_service_email(user_email)
            is_valid = verify_password(password, user.password)
        except UserNotFoundException:
            hash_password("dummy_password")
            is_valid = False
            user = None
        if not is_valid or user is None:
            raise UserCredentialInvalid("Invalid credentials")

        return UserAuthenticationReponse(email=user.email, name=user.name)
    
    def verify_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            expiration = payload.get('exp')

            if expiration and datetime.now(timezone.utc).timestamp() > expiration:
                raise UserCredentialsException('The token has been expired;')

            if payload is None:
                raise UserCredentialsException('Invalid token')

            return payload
        except InvalidTokenError as e:
            raise UserCredentialsException("Invalid Token;") from e
