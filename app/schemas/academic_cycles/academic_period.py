from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class AcademicPeriodList(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    is_current: bool
    year_id: int
    
    class Config:
        from_attributes = True