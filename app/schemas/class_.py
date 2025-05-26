from pydantic import BaseModel, field_validator
from datetime import datetime
from app.schemas.teacher import UserWithTeacherInfo
from app.schemas.student import UserWithStudentInfo
from typing import Optional, List

class ClassCreate(BaseModel):
    grade_level: int
    specialization: str
    letter: str
    
class ClassCreateDb(ClassCreate):
    year_id: int
    name: str
    
class ClassUpdateDb(ClassCreate):
    name: str
    
class ClassUpdate(ClassCreate):
    pass

class ClassList(BaseModel):
    id: int
    name: str
    year_id: int
    teacher: Optional[UserWithTeacherInfo] = None
    year_name: str
    students_count: Optional[int] = None
    specialization: Optional[str] = None
    created_at: datetime
    
class ClassConfig(BaseModel):
    specializations: List[str]
    grade_levels: List[int]
    letters: List[str]
    
    class Config:
        from_attributes = True
    
    @field_validator("grade_levels")
    def validate_grade_levels(cls, v):
        if not v:
            return ValueError("Grade levels cannot be empty")
        if len(v) != len(set(v)):
            return ValueError("Grade levels must be unique")
        if (not all(i >= 0 for i in v)):
            return ValueError("Grade levels must be positive")
        
        return v
    
    @field_validator("letters")
    def validate_letters(cls, v):
        if not v:
            return []
        if len(v) != len(set(v)):
            return ValueError("Letters must be unique")

        return v
    
    @field_validator("specializations")
    def validate_specializations(cls, v):
        if not v:
            return []
        if len(v) != len(set(v)):
            return ValueError("Specializations must be unique")
        
        return v
    
class ClassWithStudentsList(BaseModel):
    class_info: ClassList
    students: List[UserWithStudentInfo] = []
    teacher: Optional[UserWithTeacherInfo] = None
    
    class Config:
        from_attributes = True