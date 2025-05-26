from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class AcademicYearCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: datetime
    is_current: bool = False

class AcademicYearUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None

class AcademicYearList(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    is_current: bool
    created_at: datetime

class AcademicPeriodCreate(BaseModel):
    year_id: int
    name: str = Field(..., min_length=1, max_length=50)
    order_num: int = Field(..., ge=1, le=4)
    start_date: datetime
    end_date: datetime
    is_current: bool = False

class AcademicPeriodUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    order_num: Optional[int] = Field(None, ge=1, le=4)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None

class AcademicPeriodList(BaseModel):
    id: int
    year_id: int
    year_name: str
    name: str
    order_num: int
    start_date: datetime
    end_date: datetime
    is_current: bool
    created_at: datetime

class AcademicWeekCreate(BaseModel):
    period_id: int
    week_num: int = Field(..., ge=1, le=52)
    name: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: datetime
    is_holiday: bool = False

class AcademicWeekUpdate(BaseModel):
    week_num: Optional[int] = Field(None, ge=1, le=52)
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_holiday: Optional[bool] = None

class AcademicWeekList(BaseModel):
    id: int
    period_id: int
    period_name: str
    week_num: int
    name: str
    start_date: datetime
    end_date: datetime
    is_holiday: bool
    created_at: datetime