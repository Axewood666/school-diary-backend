# from datetime import date
# from typing import List, Optional

# from fastapi import HTTPException, status
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.base import BaseRepository
# from app.schemas.diary import (
#     GradeCreate,
#     HomeworkCreate,
#     LessonCreate,
#     SubjectCreate,
# )


# class DiaryService:
#     def __init__(self):
#         self.subject_repo = BaseRepository(Subject)
#         self.lesson_repo = BaseRepository(Lesson)
#         self.grade_repo = BaseRepository(Grade)
#         self.homework_repo = BaseRepository(Homework)
    
#     # Subject methods
#     async def create_subject(self, db: AsyncSession, subject_in: SubjectCreate):
#         return await self.subject_repo.create(db=db, obj_in=subject_in)
    
#     async def get_subject(self, db: AsyncSession, subject_id: int):
#         subject = await self.subject_repo.get(db=db, id=subject_id)
#         if not subject:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Subject not found",
#             )
#         return subject
    
#     async def get_all_subjects(self, db: AsyncSession, skip: int = 0, limit: int = 100):
#         return await self.subject_repo.get_multi(db=db, skip=skip, limit=limit)
    
#     # Lesson methods
#     async def create_lesson(self, db: AsyncSession, lesson_in: LessonCreate):
#         # Verify that subject exists
#         await self.get_subject(db=db, subject_id=lesson_in.subject_id)
#         return await self.lesson_repo.create(db=db, obj_in=lesson_in)
    
#     async def get_lesson(self, db: AsyncSession, lesson_id: int):
#         lesson = await self.lesson_repo.get(db=db, id=lesson_id)
#         if not lesson:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Lesson not found",
#             )
#         return lesson
    
#     async def get_lessons_by_day(self, db: AsyncSession, day_of_week: str):
#         query = select(Lesson).where(Lesson.day_of_week == day_of_week)
#         result = await db.execute(query)
#         return result.scalars().all()
    
#     # Grade methods
#     async def create_grade(self, db: AsyncSession, grade_in: GradeCreate):
#         # Verify that lesson exists
#         await self.get_lesson(db=db, lesson_id=grade_in.lesson_id)
#         return await self.grade_repo.create(db=db, obj_in=grade_in)
    
#     async def get_student_grades(self, db: AsyncSession, student_id: int):
#         query = select(Grade).where(Grade.student_id == student_id)
#         result = await db.execute(query)
#         return result.scalars().all()
    
#     # Homework methods
#     async def create_homework(self, db: AsyncSession, homework_in: HomeworkCreate):
#         # Verify that lesson exists
#         await self.get_lesson(db=db, lesson_id=homework_in.lesson_id)
#         return await self.homework_repo.create(db=db, obj_in=homework_in)
    
#     async def get_homework_by_date(self, db: AsyncSession, date: date):
#         query = select(Homework).where(Homework.due_date == date)
#         result = await db.execute(query)
#         return result.scalars().all()


# diary_service = DiaryService() 