from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional, List

class LessonTimesCreate(BaseModel):
    period_id: int
    lesson_num: int = Field(..., ge=1, le=10)
    start_time: time
    end_time: time

class LessonTimesUpdate(BaseModel):
    lesson_num: Optional[int] = Field(None, ge=1, le=10)
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class LessonTimesList(BaseModel):
    id: int
    period_id: int
    lesson_num: int
    start_time: time
    end_time: time
    created_at: datetime

class ScheduleCreate(BaseModel):
    week_id: int
    lesson_time_id: int
    class_id: int
    teacher_id: int
    subject_id: int
    day_of_week: int = Field(..., ge=1, le=7)
    location: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_replacement: bool = False
    is_cancelled: bool = False
    original_teacher_id: Optional[int] = None

class ScheduleUpdate(BaseModel):
    lesson_time_id: Optional[int] = None
    teacher_id: Optional[int] = None
    subject_id: Optional[int] = None
    day_of_week: Optional[int] = Field(None, ge=1, le=7)
    location: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_replacement: Optional[bool] = None
    is_cancelled: Optional[bool] = None
    original_teacher_id: Optional[int] = None

class ScheduleList(BaseModel):
    id: int
    week_id: int
    lesson_time_id: int
    class_id: int
    class_name: str
    teacher_id: int
    teacher_name: str
    subject_id: int
    subject_name: str
    day_of_week: int
    location: Optional[str]
    description: Optional[str]
    is_replacement: bool
    is_cancelled: bool
    original_teacher_id: Optional[int]
    original_teacher_name: Optional[str]
    lesson_num: int
    start_time: time
    end_time: time
    created_at: datetime

class HomeworkCreate(BaseModel):
    schedule_id: int
    teacher_id: int
    student_id: int
    subject_id: int
    description: str = Field(..., min_length=1, max_length=1000)
    assignment_at: datetime
    due_date: Optional[datetime] = None
    file_id: Optional[int] = None

class HomeworkUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    due_date: Optional[datetime] = None
    is_done: Optional[bool] = None
    file_id: Optional[int] = None

class HomeworkList(BaseModel):
    id: int
    schedule_id: int
    teacher_id: int
    teacher_name: str
    student_id: int
    student_name: str
    subject_id: int
    subject_name: str
    description: str
    assignment_at: datetime
    due_date: Optional[datetime]
    is_done: bool
    file_id: Optional[int]
    created_at: datetime

class GradeCreate(BaseModel):
    schedule_id: int
    student_id: int
    subject_id: int
    teacher_id: int
    homework_id: Optional[int] = None
    comment: Optional[str] = Field(None, max_length=500)
    score: int = Field(..., ge=1, le=5)

class GradeUpdate(BaseModel):
    comment: Optional[str] = Field(None, max_length=500)
    score: Optional[int] = Field(None, ge=1, le=5)

class GradeList(BaseModel):
    id: int
    schedule_id: int
    student_id: int
    student_name: str
    subject_id: int
    subject_name: str
    teacher_id: int
    teacher_name: str
    homework_id: Optional[int]
    comment: Optional[str]
    score: int
    created_at: datetime

class WeekSchedule(BaseModel):
    week_id: int
    week_name: str
    start_date: datetime
    end_date: datetime
    schedule: List[ScheduleList] = [] 