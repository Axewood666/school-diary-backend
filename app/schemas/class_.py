from pydantic import BaseModel
from datetime import datetime

class ClassCreate(BaseModel):
    name: str
    
class ClassCreateDb(ClassCreate):
    year_id: int
    
class ClassUpdate(BaseModel):
    name: str

class ClassList(BaseModel):
    id: int
    name: str
    year_id: int
    year_name: str
    created_at: datetime