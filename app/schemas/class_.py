from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class StudentClassHistoryReason(str, Enum):
    ADMISSION = "admission"
    TRANSFER = "transfer"
    RETURN = "return"

class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    grade_level: int = Field(..., ge=1, le=11)
    letter: str = Field(..., min_length=1, max_length=1)
    specialization: Optional[str] = Field(None, max_length=100)
    
class ClassCreateDb(ClassCreate):
    year_id: int
    
class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    grade_level: Optional[int] = Field(None, ge=1, le=11)
    letter: Optional[str] = Field(None, min_length=1, max_length=1)
    specialization: Optional[str] = Field(None, max_length=100)

class ClassList(BaseModel):
    id: int
    name: str
    grade_level: int
    letter: str
    specialization: Optional[str]
    year_id: int
    year_name: str
    created_at: datetime

class ClassWithStudents(ClassList):
    students_count: int = 0

class StudentClassHistoryCreate(BaseModel):
    student_id: int
    class_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    reason: Optional[StudentClassHistoryReason] = None
    is_active: bool = True

class StudentClassHistoryUpdate(BaseModel):
    end_date: Optional[datetime] = None
    reason: Optional[StudentClassHistoryReason] = None
    is_active: Optional[bool] = None

class StudentClassHistoryList(BaseModel):
    id: int
    student_id: int
    student_name: str
    class_id: int
    class_name: str
    start_date: datetime
    end_date: Optional[datetime]
    reason: Optional[StudentClassHistoryReason]
    is_active: bool
    created_at: datetime

class ClassPromotionCreate(BaseModel):
    from_class_id: int
    to_class_id: int
    promotion_date: datetime

class ClassPromotionList(BaseModel):
    id: int
    from_class_id: int
    from_class_name: str
    to_class_id: int
    to_class_name: str
    promotion_date: datetime
    created_at: datetime