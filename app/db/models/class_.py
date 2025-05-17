from app.db.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    students = relationship("Student", back_populates="class_")
    teachers = relationship("Teacher", back_populates="class_")
    lessons = relationship("Lesson", back_populates="class_")
