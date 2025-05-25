from enum import Enum as PythonEnum
from sqlalchemy import Boolean, Column, Integer, String, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timedelta

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
    admission_year = Column(Integer, nullable=True)
    parent_phone = Column(String, nullable=True)
    parent_email = Column(String, nullable=True)
    parent_fio = Column(String, nullable=True)

    user = relationship("User", back_populates="student")
    class_ = relationship("Class", back_populates="students")
    homework = relationship("Homework", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    class_history = relationship("StudentClassHistory", back_populates="student")

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
    homework = relationship("Homework", back_populates="teacher")
    grades = relationship("Grade", back_populates="teacher")
    
    schedule = relationship(
        "Schedule", 
        foreign_keys="Schedule.teacher_id", 
        back_populates="teacher"
    )
    
    replaced_schedule = relationship(
        "Schedule", 
        foreign_keys="Schedule.original_teacher_id", 
        back_populates="original_teacher"
    )
    
class UserInvite(Base):
    __tablename__ = "user_invites"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=datetime.now() + timedelta(days=7))
    role = Column(SQLEnum(UserRole), nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    is_sent = Column(Boolean, default=False)
    def is_expired(self):
        return self.expires_at < datetime.now()
    
    def is_used(self):
        return self.used_at is not None