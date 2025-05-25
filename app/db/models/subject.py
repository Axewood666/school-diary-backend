from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


# class DayOfWeek(PythonEnum):
#     MONDAY = "monday"
#     TUESDAY = "tuesday"
#     WEDNESDAY = "wednesday"
#     THURSDAY = "thursday"
#     FRIDAY = "friday"
#     SATURDAY = "saturday"


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    back_ground_color = Column(String, nullable=True)
    border_color = Column(String, nullable=True)
    text_color = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    
    teacher_subjects = relationship("TeacherSubject", back_populates="subject")
    homework = relationship("Homework", back_populates="subject")
    grades = relationship("Grade", back_populates="subject")
    schedule = relationship("Schedule", back_populates="subject")


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    is_main = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    teacher = relationship("Teacher", back_populates="teacher_subjects")
    subject = relationship("Subject", back_populates="teacher_subjects")

