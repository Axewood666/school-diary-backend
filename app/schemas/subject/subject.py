from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.schemas.user.teacher import UserWithTeacherInfo

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    back_ground_color: Optional[str] = None
    border_color: Optional[str] = None
    text_color: Optional[str] = None
    icon: Optional[str] = None
    
class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    back_ground_color: Optional[str] = None
    border_color: Optional[str] = None
    text_color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None

class SubjectList(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    back_ground_color: Optional[str] = None
    border_color: Optional[str] = None
    text_color: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class TeacherSubjectCreate(BaseModel):
    subject_id: int
    teacher_id: int

class TeacherSubjectUpdate(BaseModel):
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None

class TeacherWithSubjects(BaseModel):
    teacher: UserWithTeacherInfo
    subject: Optional[List[SubjectList]] = None