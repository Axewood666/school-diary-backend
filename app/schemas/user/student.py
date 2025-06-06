from pydantic import BaseModel
from typing import Optional
from app.schemas.user.user import UserBase, UserResponse

class StudentBase(BaseModel):
    class_id: Optional[int] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[str] = None
    parent_fio: Optional[str] = None

class Student(StudentBase):
    pass

    class Config:
        from_attributes = True

class StudentInDb(StudentBase):
    user_id: int

class StudentCreate(StudentBase):
    user_id: int

class StudentUpdate(StudentBase):
    class_id: Optional[int] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[str] = None
    parent_fio: Optional[str] = None

class UserWithStudentInfo(BaseModel):
    user_info: UserResponse
    student_info: Student

class UserStudent(UserBase, StudentBase):
    pass 