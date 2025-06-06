from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Time
from sqlalchemy.orm import relationship
from datetime import datetime

class LessonTimes(Base):
    __tablename__ = "lesson_times"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("academic_periods.id"), nullable=False)
    lesson_num = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    period = relationship("AcademicPeriod", back_populates="lesson_times")
    schedule = relationship("Schedule", back_populates="lesson_time")
class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("academic_weeks.id"), nullable=False)
    lesson_time_id = Column(Integer, ForeignKey("lesson_times.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    day_of_week = Column(Integer, nullable=False)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_replacement = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    original_teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=True)

    week = relationship("AcademicWeek", back_populates="schedule")
    lesson_time = relationship("LessonTimes", back_populates="schedule")
    class_ = relationship("Class", back_populates="schedule")
    subject = relationship("Subject", back_populates="schedule")
    homework = relationship("Homework", back_populates="schedule")
    grades = relationship("Grade", back_populates="schedule")
    
    teacher = relationship(
        "Teacher", 
        foreign_keys=[teacher_id],
        back_populates="schedule"
    )
    
    original_teacher = relationship(
        "Teacher", 
        foreign_keys=[original_teacher_id],
        back_populates="replaced_schedule"
    )    
class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    description = Column(String, nullable=False)
    assignment_at = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    is_done = Column(Boolean, default=False)    
    created_at = Column(DateTime, default=datetime.now)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    
    schedule = relationship("Schedule", back_populates="homework")
    student = relationship("Student", back_populates="homework")
    subject = relationship("Subject", back_populates="homework")
    teacher = relationship("Teacher", back_populates="homework")
    file = relationship("File", back_populates="homework")
    grades = relationship("Grade", back_populates="homework")
class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=False)
    homework_id = Column(Integer, ForeignKey("homework.id"), nullable=True)
    comment = Column(Text, nullable=True)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    schedule = relationship("Schedule", back_populates="grades")
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    teacher = relationship("Teacher", back_populates="grades")
    homework = relationship("Homework", back_populates="grades")