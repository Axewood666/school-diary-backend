from app.db.models.class_ import Class, StudentClassHistory, ClassPromotion
from app.db.models.user import Student, Teacher, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import List, Optional
from sqlalchemy import select, func
from datetime import datetime
from app.schemas.class_ import (
    ClassCreate, ClassUpdate, StudentClassHistoryCreate, 
    StudentClassHistoryUpdate, ClassPromotionCreate
)
from app.db.models.academic_cycles import AcademicYear
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from app.db.models.schedule import Schedule
from sqlalchemy import exists

class ClassRepository(BaseRepository[Class, ClassCreate, ClassUpdate]):
    async def get_classes(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                    search: Optional[str] = None, order_by: str = "created_at", 
                    order_direction: str = "desc", 
                    year: int = datetime.now().year, teacher: Teacher = None,
                    grade_level: Optional[int] = None) -> List[Class]:
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
            query = query.where(
                or_(
                    Class.name.ilike(f"%{search}%"),
                    Class.letter.ilike(f"%{search}%"),
                    Class.specialization.ilike(f"%{search}%")
                )
            )
        
        if grade_level:
            query = query.where(Class.grade_level == grade_level)
        
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

    async def get_class_with_students_count(self, db: AsyncSession, class_id: int) -> Optional[Class]:
        query = select(Class).options(
            selectinload(Class.year),
            selectinload(Class.students)
        ).where(Class.id == class_id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_classes_by_grade_level(self, db: AsyncSession, grade_level: int, 
                                       year_id: Optional[int] = None) -> List[Class]:
        query = select(Class).where(Class.grade_level == grade_level)
        if year_id:
            query = query.where(Class.year_id == year_id)
        query = query.order_by(Class.letter)
        result = await db.execute(query)
        return result.scalars().all()

class StudentClassHistoryRepository(BaseRepository[StudentClassHistory, StudentClassHistoryCreate, StudentClassHistoryUpdate]):
    async def get_student_history(self, db: AsyncSession, student_id: int) -> List[StudentClassHistory]:
        query = select(StudentClassHistory).options(
            selectinload(StudentClassHistory.class_),
            selectinload(StudentClassHistory.student).selectinload(Student.user)
        ).where(StudentClassHistory.student_id == student_id).order_by(StudentClassHistory.start_date.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_class_history(self, db: AsyncSession, class_id: int) -> List[StudentClassHistory]:
        query = select(StudentClassHistory).options(
            selectinload(StudentClassHistory.student).selectinload(Student.user),
            selectinload(StudentClassHistory.class_)
        ).where(StudentClassHistory.class_id == class_id).order_by(StudentClassHistory.start_date.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_active_class_for_student(self, db: AsyncSession, student_id: int) -> Optional[StudentClassHistory]:
        query = select(StudentClassHistory).options(
            selectinload(StudentClassHistory.class_)
        ).where(
            StudentClassHistory.student_id == student_id,
            StudentClassHistory.is_active == True
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def deactivate_previous_history(self, db: AsyncSession, student_id: int, end_date: datetime):
        """Деактивировать предыдущую историю студента"""
        query = select(StudentClassHistory).where(
            StudentClassHistory.student_id == student_id,
            StudentClassHistory.is_active == True
        )
        result = await db.execute(query)
        active_histories = result.scalars().all()
        
        for history in active_histories:
            history.is_active = False
            history.end_date = end_date
            db.add(history)
        
        await db.commit()

class ClassPromotionRepository(BaseRepository[ClassPromotion, ClassPromotionCreate, None]):
    async def get_promotions_by_class(self, db: AsyncSession, class_id: int, 
                                    is_from: bool = True) -> List[ClassPromotion]:
        if is_from:
            query = select(ClassPromotion).options(
                selectinload(ClassPromotion.to_class)
            ).where(ClassPromotion.from_class_id == class_id)
        else:
            query = select(ClassPromotion).options(
                selectinload(ClassPromotion.from_class)
            ).where(ClassPromotion.to_class_id == class_id)
        
        query = query.order_by(ClassPromotion.promotion_date.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_promotion_history(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ClassPromotion]:
        query = select(ClassPromotion).options(
            selectinload(ClassPromotion.from_class),
            selectinload(ClassPromotion.to_class)
        ).order_by(ClassPromotion.promotion_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

class_repository = ClassRepository(Class)
student_class_history_repository = StudentClassHistoryRepository(StudentClassHistory)
class_promotion_repository = ClassPromotionRepository(ClassPromotion)