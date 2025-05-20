from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    classes = relationship("Class", back_populates="year")
    periods = relationship("AcademicPeriod", back_populates="year")
class AcademicPeriod(Base):
    __tablename__ = "academic_periods"

    id = Column(Integer, primary_key=True, index=True)
    year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    name = Column(String, nullable=False)
    order_num = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    year = relationship("AcademicYear", back_populates="periods")
    weeks = relationship("AcademicWeek", back_populates="period")

class AcademicWeek(Base):
    __tablename__ = "academic_weeks"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("academic_periods.id"), nullable=False)
    week_num = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_holiday = Column(Boolean, default=False)

    period = relationship("AcademicPeriod", back_populates="weeks")
