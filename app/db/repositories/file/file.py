from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseRepository
from app.db.models.file import File
from app.schemas.file.file import FileCreate, FileUpdate


class FileRepository(BaseRepository[File, FileCreate, FileUpdate]):
    async def get_by_object_name(self, db: AsyncSession, object_name: str) -> Optional[File]:
        """Получение файла по имени объекта в хранилище"""
        query = select(self.model).where(self.model.object_name == object_name)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_bucket_and_prefix(
        self, 
        db: AsyncSession, 
        bucket_name: str, 
        prefix: str = ""
    ) -> List[File]:
        """Получение списка файлов из определенного бакета с заданным префиксом"""
        query = select(self.model).where(
            self.model.bucket_name == bucket_name,
            self.model.object_name.like(f"{prefix}%")
        )
        result = await db.execute(query)
        return result.scalars().all()


file_repository = FileRepository(File) 