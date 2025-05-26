from app.db.models.class_ import Class
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime
from app.schemas.class_ import ClassCreate, ClassUpdate
from app.db.models.academic_cycles import AcademicYear
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import or_
from app.db.models.schedule import Schedule
from app.db.models.user import Teacher, Student
from sqlalchemy import exists
from app.db.models.class_ import ClassTemplate
from app.schemas.class_ import ClassConfig
from app.db.models.class_ import StudentClassHistory, StudentClassHistoryReason

class ClassRepository(BaseRepository[Class, ClassCreate, ClassUpdate]):
    async def get_classes(self, db: AsyncSession, 
                    skip: int = 0, limit: int = 100, 
                    search: Optional[str] = None,
                    order_by: str = "created_at", 
                    order_direction: str = "desc", 
                    year: int = datetime.now().year, 
                    teacher: Teacher = None) -> List[Class]:
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
    
    async def update_class_config(self, db: AsyncSession, obj_in: ClassConfig) -> ClassConfig:
        class_config = await self.get_class_config(db=db)
    
        if not class_config:
            class_config = ClassTemplate()
            db.add(class_config)
        
        class_config.specializations = obj_in.specializations
        class_config.grade_levels = obj_in.grade_levels
        class_config.letters = obj_in.letters
        
        await db.commit()
        await db.refresh(class_config)
        
        return class_config
    
    async def has_exist_class(self, db: AsyncSession, letter: str, grade_level: int, year_id: int, class_id: int = None) -> bool:
        query = select(exists().where(Class.letter == letter, Class.grade_level == grade_level, Class.year_id == year_id, Class.id != class_id))
        result = await db.execute(query)
        return result.scalar()
    
    async def get_class_config(self, db: AsyncSession) -> ClassConfig:
        class_config = await db.scalar(select(ClassTemplate).order_by(ClassTemplate.id).limit(1))
        return class_config
    
    async def write_assign(self, db: AsyncSession, student_id: int, class_id: Optional[int] = None, reason: StudentClassHistoryReason = StudentClassHistoryReason.ADMISSION, is_active: bool = True):
        previous_history = await db.scalar(select(StudentClassHistory).where(StudentClassHistory.student_id == student_id, StudentClassHistory.is_active == True))
        if previous_history:
            previous_history.end_date = datetime.now()
            previous_history.is_active = False
            db.add(previous_history)
            await db.commit()
            await db.refresh(previous_history)
            
        history = StudentClassHistory()
        history.student_id = student_id
        history.class_id = class_id
        history.reason = reason
        history.is_active = is_active
        db.add(history)
        await db.commit()
        await db.refresh(history)
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
    
    
class_repository = ClassRepository(Class)