from enum import Enum as PythonEnum
from sqlalchemy import Boolean, Column, Integer, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

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
    
    students = relationship("Student", back_populates="user")
    teachers = relationship("Teacher", back_populates="user")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    user = relationship("User", back_populates="students")
    class_ = relationship("Class", back_populates="students")

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    user = relationship("User", back_populates="teachers")
    class_ = relationship("Class", back_populates="teachers")
    teacher_subjects = relationship("TeacherSubject", back_populates="teacher")
    lessons = relationship("Lesson", back_populates="teacher")
