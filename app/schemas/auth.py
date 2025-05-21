from typing import Optional
from app.db.models.user import UserRole
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta

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
        from_attributes = True


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


class UserInvite(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    
class UserInviteCreate(UserInvite):
    expires_at: datetime = datetime.now() + timedelta(days=7)
    class Config:
        from_attributes = True
        
class AcceptInvite(BaseModel):
    token: str
    password: str
    class Config:
        from_attributes = True

class UserInviteInfo(BaseModel):
    role: UserRole
    full_name: str
    email: EmailStr
    created_at: datetime
    expires_at: datetime
    is_sent: bool
    used_at: Optional[datetime] = None
    
class UserInviteUpdate(BaseModel):
    is_sent: Optional[bool]
    used_at: Optional[datetime]
    class Config:
        from_attributes = True