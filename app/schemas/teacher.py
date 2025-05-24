from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserBase, UserResponse

class TeacherBase(BaseModel):
    class_id: Optional[int] = None
    degree: Optional[str] = None
    experience: Optional[int] = None
    bio: Optional[str] = None

class Teacher(TeacherBase):
    pass

class TeacherInDb(TeacherBase):
    user_id: int
    id: int

class TeacherCreate(TeacherBase):
    user_id: int

class TeacherUpdate(TeacherBase):
    pass

class UserWithTeacherInfo(BaseModel):
    user_info: UserResponse
    teacher_info: Teacher

class UserTeacher(UserBase, TeacherBase):
    pass 