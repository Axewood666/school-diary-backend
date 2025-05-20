from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)

    year = relationship("AcademicYear", back_populates="classes")
    students = relationship("Student", back_populates="class_")
    teacher = relationship("Teacher", back_populates="class_")
    schedule = relationship("Schedule", back_populates="class_")