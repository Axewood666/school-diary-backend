from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

class LessonTimes(Base):
    __tablename__ = "lesson_times"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("academic_periods.id"), nullable=False)
    lesson_num = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    period = relationship("AcademicPeriod", back_populates="lesson_times")

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
    room_id = Column(String, nullable=True)
    is_replacement = Column(Boolean, default=False)
    original_teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=True)

    week = relationship("AcademicWeek", back_populates="schedule")
    lesson_time = relationship("LessonTimes", back_populates="schedule")
    class_ = relationship("Class", back_populates="schedule")
    teacher = relationship("Teacher", back_populates="schedule")
    subject = relationship("Subject", back_populates="schedule")
    original_teacher = relationship("Teacher", back_populates="original_schedule")
    replacement_teacher = relationship("Teacher", back_populates="replacement_schedule")