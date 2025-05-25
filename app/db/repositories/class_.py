from app.db.models.class_ import Class
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime
from app.schemas.class_ import ClassCreate, ClassUpdate
from app.db.models.academic_cycles import AcademicYear
from sqlalchemy.orm import joinedload

class ClassRepository(BaseRepository[Class, ClassCreate, ClassUpdate]):
    async def get_classes(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                    search: Optional[str] = None, order_by: str = "created_at", 
                    order_direction: str = "desc", 
                    year: int = datetime.now().year) -> List[Class]:
        query = select(Class).options(joinedload(Class.year).load_only(AcademicYear.name))
        if search:
            query = query.where(Class.name.ilike(f"%{search}%"))
        
        if year:
            year_id = await db.execute(
                select(AcademicYear.id).where(AcademicYear.name == str(year))
            )
            year_id = year_id.scalar()
            if year_id:
                query = query.where(Class.year_id == year_id)
        
        if order_by == "created_at":
            query = query.order_by(
                Class.created_at.desc() if order_direction == "desc" 
                else Class.created_at.asc()
            )
        elif order_by == "name":
            query = query.order_by(
                Class.name.desc() if order_direction == "desc" 
                else Class.name.asc()
            )
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
class_repository = ClassRepository(Class)