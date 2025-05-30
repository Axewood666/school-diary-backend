from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import Optional
from sqlalchemy import select
from app.schemas.academic_cycles.academic_year import AcademicYearCreate, AcademicYearUpdate
from app.db.models.academic_cycles import AcademicYear

class Academic_years_repository(BaseRepository[AcademicYear, AcademicYearCreate, AcademicYearUpdate]):
    async def get_academic_year_by_id(self, db: AsyncSession, id: int) -> Optional[AcademicYear]:
        return await self.get(db=db, id=id)
    async def get_academic_year_by_name(self, db: AsyncSession, name: str) -> Optional[AcademicYear]:
        query = select(AcademicYear).where(AcademicYear.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    async def get_current_academic_year(self, db: AsyncSession) -> Optional[AcademicYear]:
        query = select(AcademicYear).where(AcademicYear.is_current == True)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
academic_years_repository = Academic_years_repository(AcademicYear)