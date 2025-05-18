from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str
    original_filename: str
    bucket_name: str
    object_name: str
    content_type: str
    size: int


class FileCreate(FileBase):
    pass


class FileUpdate(BaseModel):
    filename: Optional[str] = None
    original_filename: Optional[str] = None


class FileInDBBase(FileBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class File(FileInDBBase):
    """Файл для ответа API"""
    url: Optional[str] = None


class FileInDB(FileInDBBase):
    """Файл в БД"""
    pass 