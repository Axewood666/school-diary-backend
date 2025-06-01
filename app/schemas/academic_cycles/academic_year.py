from pydantic import BaseModel, model_validator
from typing import Optional, List
from app.schemas.academic_cycles.academic_period import AcademicPeriodList
from datetime import datetime, date

class AcademicYearCreate(BaseModel):
    name: str
    is_current: bool
    start_date: date
    end_date: date

class AcademicYearUpdate(BaseModel):
    name: str
    is_current: bool
    start_date: date
    end_date: date
    
class AcademicYearList(BaseModel):
    id: int
    name: str
    is_current: bool
    start_date: date
    end_date: date
    created_at: datetime
    periods: Optional[List[AcademicPeriodList]] = None
    
    @model_validator(mode='before')
    @classmethod
    def convert_periods(cls, data):
        if hasattr(data, '__dict__'):
            data_dict = {}
            for key, value in data.__dict__.items():
                if key.startswith('_'):
                    continue
                data_dict[key] = value
            data = data_dict
            
        if isinstance(data, dict) and 'periods' in data and data['periods']:
            periods = data['periods']
            if periods and hasattr(periods[0], '__dict__'):
                data['periods'] = [AcademicPeriodList.model_validate(period) for period in periods]
        
        return data
    
    class Config:
        from_attributes = True