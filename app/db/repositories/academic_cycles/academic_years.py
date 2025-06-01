from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import Optional
from sqlalchemy import select
from app.schemas.academic_cycles.academic_year import AcademicYearCreate, AcademicYearUpdate
from app.db.models.academic_cycles import AcademicYear
from app.schemas.academic_cycles.academic_year import AcademicYearList
from sqlalchemy.orm import joinedload
from typing import List
class Academic_years_repository(BaseRepository[AcademicYear, AcademicYearCreate, AcademicYearUpdate]):
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> List[AcademicYear]:
        query = select(AcademicYear).offset(skip).limit(limit).options(joinedload(AcademicYear.periods))
        query = query.order_by(AcademicYear.name.desc())
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    async def get_academic_year_by_id(self, db: AsyncSession, id: int) -> Optional[AcademicYear]:
        return await self.get(db=db, id=id)
    async def get_academic_year_by_name(self, db: AsyncSession, name: str) -> Optional[AcademicYear]:
        query = select(AcademicYear).where(AcademicYear.name == name).options(joinedload(AcademicYear.periods))
        result = await db.execute(query)
        return result.unique().scalar_one_or_none()
    async def get_current_academic_year(self, db: AsyncSession) -> Optional[AcademicYear]:
        query = select(AcademicYear).where(AcademicYear.is_current == True).options(joinedload(AcademicYear.periods))
        result = await db.execute(query)
        return result.unique().scalar_one_or_none()
    async def get_with_periods(self, db: AsyncSession, academic_year_id: int) -> Optional[AcademicYear]:
        query = select(AcademicYear).where(AcademicYear.id == academic_year_id).options(joinedload(AcademicYear.periods))
        result = await db.execute(query)
        return result.unique().scalar_one_or_none()
    
academic_years_repository = Academic_years_repository(AcademicYear)