from pydantic import BaseModel, EmailStr
from typing import Optional
from app.db.models.user import UserRole

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

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
    id: int

class UserInDB(UserInDBBase):
    hashed_password: str

class UserDeactivateData(BaseModel):
    is_deactivated: bool 