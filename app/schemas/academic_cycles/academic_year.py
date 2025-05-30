from pydantic import BaseModel

class AcademicYearCreate(BaseModel):
    name: str

class AcademicYearUpdate(BaseModel):
    name: str