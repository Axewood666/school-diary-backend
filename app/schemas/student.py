from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserBase, UserResponse

class StudentBase(BaseModel):
    class_id: Optional[int] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[str] = None
    parent_fio: Optional[str] = None

class Student(StudentBase):
    pass

class StudentInDb(StudentBase):
    user_id: int
    id: int

class StudentCreate(StudentBase):
    user_id: int

class StudentUpdate(StudentBase):
    pass

class UserWithStudentInfo(BaseModel):
    user_info: UserResponse
    student_info: Student

class UserStudent(UserBase, StudentBase):
    pass 