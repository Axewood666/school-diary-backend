from app.db.models.class_ import Class
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime
from app.schemas.class_ import ClassCreate, ClassUpdate
from app.db.models.academic_cycles import AcademicYear
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from app.db.models.schedule import Schedule
from app.db.models.user import Teacher
from sqlalchemy import exists
class ClassRepository(BaseRepository[Class, ClassCreate, ClassUpdate]):
    async def get_classes(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                    search: Optional[str] = None, order_by: str = "created_at", 
                    order_direction: str = "desc", 
                    year: int = datetime.now().year, teacher: Teacher = None) -> List[Class]:
        query = select(Class).options(
            selectinload(Class.year).load_only(AcademicYear.name)
        )

        if teacher is not None:
            conditions = [
                exists().where(
                    (Schedule.teacher_id == teacher.user_id) & 
                    (Schedule.class_id == Class.id)
                )]
            if teacher.class_id is not None:
                conditions.append(Class.id == teacher.class_id)
            query = query.where(or_(*conditions))

        if search:
            query = query.where(Class.name.ilike(f"%{search}%"))
        
        if year:
            year_id = await db.scalar(
                select(AcademicYear.id).where(AcademicYear.name == str(year))
            )
            if year_id is not None:
                query = query.where(Class.year_id == year_id)
        
        order_column = getattr(Class, order_by, Class.created_at)
        if order_direction == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
class_repository = ClassRepository(Class)