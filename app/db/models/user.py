from enum import Enum as PythonEnum
from sqlalchemy import Boolean, Column, Integer, String, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
class UserRole(PythonEnum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    
    student = relationship("Student", back_populates="user")
    teacher = relationship("Teacher", back_populates="user")

class Student(Base):
    __tablename__ = "students"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    parent_phone = Column(String, nullable=True)
    parent_email = Column(String, nullable=True)
    parent_fio = Column(String, nullable=True)

    user = relationship("User", back_populates="student")
    class_ = relationship("Class", back_populates="students")

class Teacher(Base):
    __tablename__ = "teachers"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    degree = Column(String, nullable=True)
    experience = Column(Integer, nullable=True)
    bio = Column(String, nullable=True)

    user = relationship("User", back_populates="teacher")
    class_ = relationship("Class", back_populates="teacher")
    teacher_subjects = relationship("TeacherSubject", back_populates="teacher")
    # lessons = relationship("Lesson", back_populates="teacher")
