from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.types import Enum as SQLAlchemyEnum
from enum import Enum as PythonEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession

class StudentClassHistoryReason(PythonEnum):
    ADMISSION = "admission"
    TRANSFER = "transfer"
    RETURN = "return"

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=False)
    letter = Column(String(1), nullable=False)
    specialization = Column(String, nullable=True)
    year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    year = relationship("AcademicYear", back_populates="classes")
    students = relationship("Student", back_populates="class_")
    teacher = relationship("Teacher", back_populates="class_", uselist=False)
    schedule = relationship("Schedule", back_populates="class_")
    class_history = relationship("StudentClassHistory", back_populates="class_")
    promotions_from = relationship("ClassPromotion", back_populates="from_class", foreign_keys="[ClassPromotion.from_class_id]")
    promotions_to = relationship("ClassPromotion", back_populates="to_class", foreign_keys="[ClassPromotion.to_class_id]")
    
    @property
    def students_count(self):
        return len(self.students)

class StudentClassHistory(Base):
    __tablename__ = "student_class_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    start_date = Column(DateTime, nullable=False, default=datetime.now)
    end_date = Column(DateTime, nullable=True)
    reason = Column(SQLAlchemyEnum(StudentClassHistoryReason), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    class_ = relationship("Class", back_populates="class_history")
    student = relationship("Student", back_populates="class_history")

class ClassPromotion(Base):
    __tablename__ = "class_promotions"

    id = Column(Integer, primary_key=True, index=True)
    from_class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    to_class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    promotion_date = Column(DateTime, nullable=False, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

    from_class = relationship("Class", foreign_keys=[from_class_id], back_populates="promotions_from")
    to_class = relationship("Class", foreign_keys=[to_class_id], back_populates="promotions_to")
    
    def write_promotion(self, db: AsyncSession, from_class_id: int, to_class_id: int):
        self.from_class_id = from_class_id
        self.to_class_id = to_class_id
        db.add(self)
        db.commit()
    
class ClassTemplate(Base):
    __tablename__ = "class_templates"

    id = Column(Integer, primary_key=True, index=True)
    grade_levels = Column(ARRAY(Integer), nullable=False)
    letters = Column(ARRAY(String(1)), nullable=False)
    specializations = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime, default=datetime.now)