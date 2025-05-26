from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime
from app.schemas.academic_cycles import AcademicYearCreate, AcademicYearUpdate
from app.db.models.academic_cycles import AcademicYear, AcademicPeriod, AcademicWeek

class AcademicCyclesRepository(BaseRepository[AcademicYear, AcademicYearCreate, AcademicYearUpdate]):
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
    
    async def get_current_academic_period(self, db: AsyncSession) -> Optional[AcademicPeriod]:
        query = select(AcademicPeriod).where(AcademicPeriod.is_current == True)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_academic_periods_by_year(self, db: AsyncSession, year_id: int) -> List[AcademicPeriod]:
        query = select(AcademicPeriod).where(AcademicPeriod.year_id == year_id).order_by(AcademicPeriod.order_num)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_academic_weeks_by_period(self, db: AsyncSession, period_id: int) -> List[AcademicWeek]:
        query = select(AcademicWeek).where(AcademicWeek.period_id == period_id).order_by(AcademicWeek.week_num)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_current_academic_week(self, db: AsyncSession) -> Optional[AcademicWeek]:
        current_date = datetime.now()
        query = select(AcademicWeek).where(
            AcademicWeek.start_date <= current_date,
            AcademicWeek.end_date >= current_date
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
academic_cycles_repository = AcademicCyclesRepository(AcademicYear)