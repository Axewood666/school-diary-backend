from app.db.models.schedule import Schedule, LessonTimes, Homework, Grade
from app.db.models.academic_cycles import AcademicWeek, AcademicPeriod
from app.db.models.class_ import Class
from app.db.models.subject import Subject
from app.db.models.user import Teacher, Student, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import List, Optional
from sqlalchemy import select, and_
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, LessonTimesCreate, LessonTimesUpdate,
    HomeworkCreate, HomeworkUpdate, GradeCreate, GradeUpdate
)
from sqlalchemy.orm import selectinload

class LessonTimesRepository(BaseRepository[LessonTimes, LessonTimesCreate, LessonTimesUpdate]):
    async def get_by_period(self, db: AsyncSession, period_id: int) -> List[LessonTimes]:
        query = select(LessonTimes).where(LessonTimes.period_id == period_id).order_by(LessonTimes.lesson_num)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_period_and_lesson_num(self, db: AsyncSession, period_id: int, lesson_num: int) -> Optional[LessonTimes]:
        query = select(LessonTimes).where(
            LessonTimes.period_id == period_id,
            LessonTimes.lesson_num == lesson_num
        )
        result = await db.execute(query)
        return result.scalars().first()

class ScheduleRepository(BaseRepository[Schedule, ScheduleCreate, ScheduleUpdate]):
    async def get_schedule_by_week_and_class(self, db: AsyncSession, week_id: int, class_id: int) -> List[Schedule]:
        query = select(Schedule).options(
            selectinload(Schedule.lesson_time),
            selectinload(Schedule.subject),
            selectinload(Schedule.teacher).selectinload(Teacher.user),
            selectinload(Schedule.original_teacher).selectinload(Teacher.user),
            selectinload(Schedule.class_)
        ).where(
            Schedule.week_id == week_id,
            Schedule.class_id == class_id
        ).order_by(Schedule.day_of_week, Schedule.lesson_time_id)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_schedule_by_week_and_teacher(self, db: AsyncSession, week_id: int, teacher_id: int) -> List[Schedule]:
        query = select(Schedule).options(
            selectinload(Schedule.lesson_time),
            selectinload(Schedule.subject),
            selectinload(Schedule.class_),
            selectinload(Schedule.original_teacher).selectinload(Teacher.user)
        ).where(
            Schedule.week_id == week_id,
            Schedule.teacher_id == teacher_id
        ).order_by(Schedule.day_of_week, Schedule.lesson_time_id)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_schedule_by_date_range(self, db: AsyncSession, class_id: Optional[int] = None, 
                                       teacher_id: Optional[int] = None, 
                                       start_week_id: Optional[int] = None,
                                       end_week_id: Optional[int] = None) -> List[Schedule]:
        query = select(Schedule).options(
            selectinload(Schedule.lesson_time),
            selectinload(Schedule.subject),
            selectinload(Schedule.teacher).selectinload(Teacher.user),
            selectinload(Schedule.class_),
            selectinload(Schedule.week)
        )

        conditions = []
        if class_id:
            conditions.append(Schedule.class_id == class_id)
        if teacher_id:
            conditions.append(Schedule.teacher_id == teacher_id)
        if start_week_id:
            conditions.append(Schedule.week_id >= start_week_id)
        if end_week_id:
            conditions.append(Schedule.week_id <= end_week_id)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Schedule.week_id, Schedule.day_of_week, Schedule.lesson_time_id)
        result = await db.execute(query)
        return result.scalars().all()

class HomeworkRepository(BaseRepository[Homework, HomeworkCreate, HomeworkUpdate]):
    async def get_homework_by_student(self, db: AsyncSession, student_id: int, 
                                    skip: int = 0, limit: int = 100,
                                    is_done: Optional[bool] = None) -> List[Homework]:
        query = select(Homework).options(
            selectinload(Homework.subject),
            selectinload(Homework.teacher).selectinload(Teacher.user),
            selectinload(Homework.schedule).selectinload(Schedule.lesson_time)
        ).where(Homework.student_id == student_id)

        if is_done is not None:
            query = query.where(Homework.is_done == is_done)

        query = query.order_by(Homework.due_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_homework_by_teacher(self, db: AsyncSession, teacher_id: int,
                                    skip: int = 0, limit: int = 100) -> List[Homework]:
        query = select(Homework).options(
            selectinload(Homework.subject),
            selectinload(Homework.student).selectinload(Student.user),
            selectinload(Homework.schedule).selectinload(Schedule.lesson_time)
        ).where(Homework.teacher_id == teacher_id)

        query = query.order_by(Homework.assignment_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_homework_by_class_and_subject(self, db: AsyncSession, class_id: int, 
                                              subject_id: int, skip: int = 0, limit: int = 100) -> List[Homework]:
        query = select(Homework).options(
            selectinload(Homework.student).selectinload(Student.user),
            selectinload(Homework.teacher).selectinload(Teacher.user),
            selectinload(Homework.schedule).selectinload(Schedule.lesson_time)
        ).join(Schedule).where(
            Schedule.class_id == class_id,
            Homework.subject_id == subject_id
        )

        query = query.order_by(Homework.assignment_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

class GradeRepository(BaseRepository[Grade, GradeCreate, GradeUpdate]):
    async def get_grades_by_student(self, db: AsyncSession, student_id: int,
                                  subject_id: Optional[int] = None,
                                  skip: int = 0, limit: int = 100) -> List[Grade]:
        query = select(Grade).options(
            selectinload(Grade.subject),
            selectinload(Grade.teacher).selectinload(Teacher.user),
            selectinload(Grade.schedule).selectinload(Schedule.lesson_time)
        ).where(Grade.student_id == student_id)

        if subject_id:
            query = query.where(Grade.subject_id == subject_id)

        query = query.order_by(Grade.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_grades_by_teacher(self, db: AsyncSession, teacher_id: int,
                                  class_id: Optional[int] = None,
                                  subject_id: Optional[int] = None,
                                  skip: int = 0, limit: int = 100) -> List[Grade]:
        query = select(Grade).options(
            selectinload(Grade.subject),
            selectinload(Grade.student).selectinload(Student.user),
            selectinload(Grade.schedule).selectinload(Schedule.lesson_time)
        ).where(Grade.teacher_id == teacher_id)

        if class_id:
            query = query.join(Schedule).where(Schedule.class_id == class_id)
        if subject_id:
            query = query.where(Grade.subject_id == subject_id)

        query = query.order_by(Grade.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_grades_by_class_and_subject(self, db: AsyncSession, class_id: int,
                                            subject_id: int, skip: int = 0, limit: int = 100) -> List[Grade]:
        query = select(Grade).options(
            selectinload(Grade.student).selectinload(Student.user),
            selectinload(Grade.teacher).selectinload(Teacher.user),
            selectinload(Grade.schedule).selectinload(Schedule.lesson_time)
        ).join(Schedule).where(
            Schedule.class_id == class_id,
            Grade.subject_id == subject_id
        )

        query = query.order_by(Grade.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

lesson_times_repository = LessonTimesRepository(LessonTimes)
schedule_repository = ScheduleRepository(Schedule)
homework_repository = HomeworkRepository(Homework)
grade_repository = GradeRepository(Grade) 