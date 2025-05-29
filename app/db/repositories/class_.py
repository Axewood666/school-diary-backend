from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.db.base import BaseRepository
from app.db.models.class_ import Class
from app.db.models.academic_cycles import AcademicYear
from app.db.models.schedule import Schedule
from app.db.models.user import Teacher, Student
from app.schemas.class_ import ClassCreate, ClassUpdate


class ClassRepository(BaseRepository[Class, ClassCreate, ClassUpdate]):
    async def get_classes(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        order_by: str = "created_at", 
        order_direction: str = "desc", 
        year: int = datetime.now().year, 
        teacher: Teacher = None
    ) -> List[Class]:
        query = select(Class).options(
            selectinload(Class.year).load_only(AcademicYear.name),
            selectinload(Class.teacher).selectinload(Teacher.user),
            selectinload(Class.students).load_only(Student.user_id)
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
        return result.unique().scalars().all()

    async def has_exist_class(
        self, 
        db: AsyncSession, 
        letter: str, 
        grade_level: int, 
        year_id: int, 
        class_id: int = None
    ) -> bool:
        query = select(exists().where(
            Class.letter == letter, 
            Class.grade_level == grade_level, 
            Class.year_id == year_id, 
            Class.id != class_id
        ))
        result = await db.execute(query)
        return result.scalar()

    async def get_with_relations(self, db: AsyncSession, id: int) -> Class:
        result = await db.execute(
            select(Class)
            .options(
                selectinload(Class.students).joinedload(Student.user),
                joinedload(Class.teacher).joinedload(Teacher.user),
                joinedload(Class.year).load_only(AcademicYear.name)
            )
            .where(Class.id == id)
        )
        
        result = result.scalar_one_or_none()
        return result

    async def get_existing_letters(self, db: AsyncSession, grade_level: int) -> List[str]:
        query = select(Class.letter).where(Class.grade_level == grade_level)
        result = await db.execute(query)
        return result.scalars().all()


class_repository = ClassRepository(Class)