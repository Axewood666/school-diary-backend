from pydantic import BaseModel
from typing import Optional
from pydantic import EmailStr
from app.db.models.user import UserRole

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int

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

class Student(BaseModel):
    class_id: Optional[int] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[str] = None
    parent_fio: Optional[str] = None

class Teacher(BaseModel):
    class_id: Optional[int] = None
    degree: Optional[str] = None
    experience: Optional[int] = None
    bio: Optional[str] = None

class Admin(BaseModel):
    pass

class StudentInDb(Student):
    user_id: int
    class_id: Optional[int] = None

class TeacherInDb(Teacher):
    user_id: int
    class_id: Optional[int] = None
    
class UserStudent(UserBase, Student):
    pass

class UserTeacher(UserBase, Teacher):
    pass

