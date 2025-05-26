from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    back_ground_color: Optional[str] = Field(None, max_length=7)
    border_color: Optional[str] = Field(None, max_length=7)
    text_color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)

class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    back_ground_color: Optional[str] = Field(None, max_length=7)
    border_color: Optional[str] = Field(None, max_length=7)
    text_color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)

class SubjectList(BaseModel):
    id: int
    name: str
    back_ground_color: Optional[str]
    border_color: Optional[str]
    text_color: Optional[str]
    icon: Optional[str]
    created_at: datetime

class TeacherSubjectCreate(BaseModel):
    teacher_id: int
    subject_id: int
    is_main: bool = False

class TeacherSubjectUpdate(BaseModel):
    is_main: Optional[bool] = None

class TeacherSubjectList(BaseModel):
    id: int
    teacher_id: int
    subject_id: int
    subject_name: str
    is_main: bool
    created_at: datetime

class SubjectWithTeachers(SubjectList):
    teachers: List[TeacherSubjectList] = [] 