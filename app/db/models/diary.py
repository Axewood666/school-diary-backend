from datetime import date
from enum import Enum as PythonEnum

from sqlalchemy import Column, Date, Enum as SQLEnum, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship

from app.db.base import Base


class DayOfWeek(PythonEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    lessons = relationship("Lesson", back_populates="subject")
    teacher_subjects = relationship("TeacherSubject", back_populates="subject")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    classroom = Column(String)
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    subject = relationship("Subject", back_populates="lessons")
    grades = relationship("Grade", back_populates="lesson")
    homework = relationship("Homework", back_populates="lesson")
    teacher = relationship("Teacher", back_populates="lessons")
    class_ = relationship("Class", back_populates="lessons")


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    grade_date = Column(Date, nullable=False, default=date.today)
    value = Column(Integer, nullable=False)
    comment = Column(String)
    
    lesson = relationship("Lesson", back_populates="grades")


class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    assigned_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    
    lesson = relationship("Lesson", back_populates="homework") 


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    teacher = relationship("Teacher", back_populates="teacher_subjects")
    subject = relationship("Subject", back_populates="teacher_subjects")
