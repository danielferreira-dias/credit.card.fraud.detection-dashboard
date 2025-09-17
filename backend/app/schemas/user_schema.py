from pydantic import BaseModel, EmailStr
from app.schemas.auth_schema import TokenResponse

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

    def __repr__(self):
        return f"<UserCreate(email={self.email}, name={self.name})>"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        orm_mode = True
    
    def __repr__(self):
        return f"<UserResponse(id={self.id}, email={self.email}, name={self.name})>"

class RegisterResponse(BaseModel):
    user: UserResponse
    token: TokenResponse

class UserSchema(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserAuthenticationReponse(BaseModel):
    email: EmailStr
    name: str

class UserLoginAuthentication(BaseModel):
    email: EmailStr
    password: str

class UserRegisterSchema(BaseModel):
    email: EmailStr
    name: str 
    password: str
    confirm_password: str