from typing import Optional
from app.db.models.user import UserRole
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: UserRole


class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str
