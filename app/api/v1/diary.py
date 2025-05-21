# from typing import List

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.dependencies import get_current_user
# from app.db.session import get_db
# from app.schemas.auth import User
# from app.schemas.diary import (
#     Grade,
#     GradeCreate,
#     Homework,
#     HomeworkCreate,
#     Lesson,
#     LessonCreate,
#     Subject,
#     SubjectCreate,
# )
# from app.services.diary import diary_service

# router = APIRouter(tags=["diary"])


# # Subject endpoints
# @router.post("/subjects", response_model=Subject)
# async def create_subject(
#     subject_in: SubjectCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """Create a new subject (admin only)"""
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions",
#         )
#     return await diary_service.create_subject(db=db, subject_in=subject_in)


# @router.get("/subjects", response_model=List[Subject])
# async def read_subjects(
#     skip: int = 0,
#     limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     _: User = Depends(get_current_user),
# ):
#     """Get all subjects"""
#     return await diary_service.get_all_subjects(db=db, skip=skip, limit=limit)


# # Lesson endpoints
# @router.post("/lessons", response_model=Lesson)
# async def create_lesson(
#     lesson_in: LessonCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """Create a new lesson (admin only)"""
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions",
#         )
#     return await diary_service.create_lesson(db=db, lesson_in=lesson_in)


# @router.get("/lessons/day/{day_of_week}", response_model=List[Lesson])
# async def read_lessons_by_day(
#     day_of_week: str,
#     db: AsyncSession = Depends(get_db),
#     _: User = Depends(get_current_user),
# ):
#     """Get lessons by day of week"""
#     return await diary_service.get_lessons_by_day(db=db, day_of_week=day_of_week)


# # Grade endpoints
# @router.post("/grades", response_model=Grade)
# async def create_grade(
#     grade_in: GradeCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """Create a new grade (admin only)"""
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions",
#         )
#     return await diary_service.create_grade(db=db, grade_in=grade_in)


# @router.get("/grades/student/{student_id}", response_model=List[Grade])
# async def read_student_grades(
#     student_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """Get student grades (student can only see their own grades)"""
#     if not current_user.is_superuser and current_user.id != student_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions",
#         )
#     return await diary_service.get_student_grades(db=db, student_id=student_id)


# # Homework endpoints
# @router.post("/homework", response_model=Homework)
# async def create_homework(
#     homework_in: HomeworkCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """Create a new homework (admin only)"""
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions",
#         )
#     return await diary_service.create_homework(db=db, homework_in=homework_in)


# @router.get("/homework/date/{date}", response_model=List[Homework])
# async def read_homework_by_date(
#     date: str,
#     db: AsyncSession = Depends(get_db),
#     _: User = Depends(get_current_user),
# ):
#     """Get homework by date"""
#     return await diary_service.get_homework_by_date(db=db, date=date) 