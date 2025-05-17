from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel

from app.db.models.diary import DayOfWeek


# Subject schemas
class SubjectBase(BaseModel):
    name: str


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(SubjectBase):
    pass


class SubjectInDBBase(SubjectBase):
    id: int

    class Config:
        orm_mode = True


class Subject(SubjectInDBBase):
    pass


# Lesson schemas
class LessonBase(BaseModel):
    subject_id: int
    teacher_name: str
    classroom: Optional[str] = None
    day_of_week: DayOfWeek
    start_time: time
    end_time: time


class LessonCreate(LessonBase):
    pass


class LessonUpdate(LessonBase):
    subject_id: Optional[int] = None
    teacher_name: Optional[str] = None
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class LessonInDBBase(LessonBase):
    id: int
    subject: Subject

    class Config:
        orm_mode = True


class Lesson(LessonInDBBase):
    pass


# Grade schemas
class GradeBase(BaseModel):
    student_id: int
    lesson_id: int
    grade_date: date
    value: int
    comment: Optional[str] = None


class GradeCreate(GradeBase):
    pass


class GradeUpdate(GradeBase):
    student_id: Optional[int] = None
    lesson_id: Optional[int] = None
    grade_date: Optional[date] = None
    value: Optional[int] = None


class GradeInDBBase(GradeBase):
    id: int
    lesson: Lesson

    class Config:
        orm_mode = True


class Grade(GradeInDBBase):
    pass


# Homework schemas
class HomeworkBase(BaseModel):
    lesson_id: int
    assigned_date: date
    due_date: date
    description: str


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkUpdate(HomeworkBase):
    lesson_id: Optional[int] = None
    assigned_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = None


class HomeworkInDBBase(HomeworkBase):
    id: int

    class Config:
        orm_mode = True


class Homework(HomeworkInDBBase):
    lesson: Lesson 