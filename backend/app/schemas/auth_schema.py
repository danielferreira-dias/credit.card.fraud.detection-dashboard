from dataclasses import dataclass
from pydantic import BaseModel, EmailStr

@dataclass
class Token:
    access_token: str
    token_type: str

class TokenResponse(BaseModel):
    user_email: EmailStr
    name: str
    token: Token

class GoogleAuthRequest(BaseModel):
    token: str