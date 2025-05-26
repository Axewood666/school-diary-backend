from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Optional

from app.schemas.base import error_response, BaseResponse, ErrorResponse, success_response
from app.schemas.user import UserRole, User
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleList, WeekSchedule,
    LessonTimesCreate, LessonTimesUpdate, LessonTimesList,
    HomeworkCreate, HomeworkUpdate, HomeworkList,
    GradeCreate, GradeUpdate, GradeList
)

from app.core.dependencies import get_db, get_current_user
from app.core.logger import setup_logging
from app.db.repositories.schedule import (
    schedule_repository, lesson_times_repository, 
    homework_repository, grade_repository
)
from app.db.repositories.academic_cycles import academic_cycles_repository
from app.db.repositories.class_ import class_repository
from app.db.repositories.subject import subject_repository
from app.db.repositories.user import user_repository

import logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["schedule"])

# Lesson Times endpoints
@router.get("/lesson-times", response_model=Union[BaseResponse[List[LessonTimesList]], ErrorResponse])
async def get_lesson_times(
    period_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить время уроков"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        if period_id:
            lesson_times = await lesson_times_repository.get_by_period(db=db, period_id=period_id)
        else:
            # Получаем текущий период
            current_period = await academic_cycles_repository.get_current_academic_period(db=db)
            if not current_period:
                return error_response(
                    message="Текущий учебный период не найден",
                    error_code="CURRENT_PERIOD_NOT_FOUND"
                )
            lesson_times = await lesson_times_repository.get_by_period(db=db, period_id=current_period.id)

        lesson_times_list = [
            LessonTimesList(
                id=lt.id,
                period_id=lt.period_id,
                lesson_num=lt.lesson_num,
                start_time=lt.start_time,
                end_time=lt.end_time,
                created_at=lt.created_at
            ) for lt in lesson_times
        ]

        return success_response(
            data=lesson_times_list,
            message="Время уроков успешно получено"
        )
    except Exception as e:
        logger.error(f"GET_LESSON_TIMES_ERROR: {e}")
        return error_response(
            message="Не удалось получить время уроков",
            error_code="GET_LESSON_TIMES_ERROR"
        )

@router.post("/lesson-times", response_model=Union[BaseResponse[LessonTimesList], ErrorResponse])
async def create_lesson_time(
    lesson_time_create: LessonTimesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать время урока"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Проверяем, не существует ли уже такое время урока
        existing = await lesson_times_repository.get_by_period_and_lesson_num(
            db=db, period_id=lesson_time_create.period_id, lesson_num=lesson_time_create.lesson_num
        )
        if existing:
            return error_response(
                message="Время урока с таким номером уже существует",
                error_code="LESSON_TIME_ALREADY_EXISTS"
            )

        lesson_time = await lesson_times_repository.create(db=db, obj_in=lesson_time_create)

        return success_response(
            data=LessonTimesList(
                id=lesson_time.id,
                period_id=lesson_time.period_id,
                lesson_num=lesson_time.lesson_num,
                start_time=lesson_time.start_time,
                end_time=lesson_time.end_time,
                created_at=lesson_time.created_at
            ),
            message="Время урока успешно создано"
        )
    except Exception as e:
        logger.error(f"CREATE_LESSON_TIME_ERROR: {e}")
        return error_response(
            message="Не удалось создать время урока",
            error_code="CREATE_LESSON_TIME_ERROR"
        )

# Schedule endpoints
@router.get("/", response_model=Union[BaseResponse[List[ScheduleList]], ErrorResponse])
async def get_schedule(
    week_id: Optional[int] = None,
    class_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    start_week_id: Optional[int] = None,
    end_week_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить расписание"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Если это студент, он может видеть только расписание своего класса
        if current_user.role == UserRole.STUDENT:
            student = await user_repository.get_user_student(db=db, user_id=current_user.id)
            if not student or not student.class_id:
                return error_response(
                    message="Студент не привязан к классу",
                    error_code="STUDENT_NOT_ASSIGNED_TO_CLASS"
                )
            class_id = student.class_id

        # Если это учитель, он может видеть только свое расписание (если не указан class_id)
        if current_user.role == UserRole.TEACHER and not class_id:
            teacher_id = current_user.id

        if week_id and class_id:
            schedule_items = await schedule_repository.get_schedule_by_week_and_class(
                db=db, week_id=week_id, class_id=class_id
            )
        elif week_id and teacher_id:
            schedule_items = await schedule_repository.get_schedule_by_week_and_teacher(
                db=db, week_id=week_id, teacher_id=teacher_id
            )
        else:
            schedule_items = await schedule_repository.get_schedule_by_date_range(
                db=db, class_id=class_id, teacher_id=teacher_id,
                start_week_id=start_week_id, end_week_id=end_week_id
            )

        schedule_list = []
        for item in schedule_items:
            schedule_list.append(ScheduleList(
                id=item.id,
                week_id=item.week_id,
                lesson_time_id=item.lesson_time_id,
                class_id=item.class_id,
                class_name=item.class_.name,
                teacher_id=item.teacher_id,
                teacher_name=item.teacher.user.full_name,
                subject_id=item.subject_id,
                subject_name=item.subject.name,
                day_of_week=item.day_of_week,
                location=item.location,
                description=item.description,
                is_replacement=item.is_replacement,
                is_cancelled=item.is_cancelled,
                original_teacher_id=item.original_teacher_id,
                original_teacher_name=item.original_teacher.user.full_name if item.original_teacher else None,
                lesson_num=item.lesson_time.lesson_num,
                start_time=item.lesson_time.start_time,
                end_time=item.lesson_time.end_time,
                created_at=item.created_at
            ))

        return success_response(
            data=schedule_list,
            message="Расписание успешно получено"
        )
    except Exception as e:
        logger.error(f"GET_SCHEDULE_ERROR: {e}")
        return error_response(
            message="Не удалось получить расписание",
            error_code="GET_SCHEDULE_ERROR"
        )

@router.post("/", response_model=Union[BaseResponse[ScheduleList], ErrorResponse])
async def create_schedule_item(
    schedule_create: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать элемент расписания"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Проверяем существование всех связанных объектов
        lesson_time = await lesson_times_repository.get(db=db, id=schedule_create.lesson_time_id)
        if not lesson_time:
            return error_response(
                message="Время урока не найдено",
                error_code="LESSON_TIME_NOT_FOUND"
            )

        class_ = await class_repository.get(db=db, id=schedule_create.class_id)
        if not class_:
            return error_response(
                message="Класс не найден",
                error_code="CLASS_NOT_FOUND"
            )

        teacher = await user_repository.get_user_teacher(db=db, user_id=schedule_create.teacher_id)
        if not teacher:
            return error_response(
                message="Учитель не найден",
                error_code="TEACHER_NOT_FOUND"
            )

        subject = await subject_repository.get(db=db, id=schedule_create.subject_id)
        if not subject:
            return error_response(
                message="Предмет не найден",
                error_code="SUBJECT_NOT_FOUND"
            )

        schedule_item = await schedule_repository.create(db=db, obj_in=schedule_create)

        return success_response(
            data=ScheduleList(
                id=schedule_item.id,
                week_id=schedule_item.week_id,
                lesson_time_id=schedule_item.lesson_time_id,
                class_id=schedule_item.class_id,
                class_name=class_.name,
                teacher_id=schedule_item.teacher_id,
                teacher_name=teacher.user.full_name,
                subject_id=schedule_item.subject_id,
                subject_name=subject.name,
                day_of_week=schedule_item.day_of_week,
                location=schedule_item.location,
                description=schedule_item.description,
                is_replacement=schedule_item.is_replacement,
                is_cancelled=schedule_item.is_cancelled,
                original_teacher_id=schedule_item.original_teacher_id,
                original_teacher_name=None,
                lesson_num=lesson_time.lesson_num,
                start_time=lesson_time.start_time,
                end_time=lesson_time.end_time,
                created_at=schedule_item.created_at
            ),
            message="Элемент расписания успешно создан"
        )
    except Exception as e:
        logger.error(f"CREATE_SCHEDULE_ITEM_ERROR: {e}")
        return error_response(
            message="Не удалось создать элемент расписания",
            error_code="CREATE_SCHEDULE_ITEM_ERROR"
        )

@router.patch("/{schedule_id}", response_model=Union[BaseResponse[ScheduleList], ErrorResponse])
async def update_schedule_item(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить элемент расписания"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        schedule_item = await schedule_repository.get(db=db, id=schedule_id)
        if not schedule_item:
            return error_response(
                message="Элемент расписания не найден",
                error_code="SCHEDULE_ITEM_NOT_FOUND"
            )

        schedule_item = await schedule_repository.update(db=db, db_obj=schedule_item, obj_in=schedule_update)

        # Получаем обновленные данные с связанными объектами
        updated_item = await schedule_repository.get(db=db, id=schedule_id)
        
        return success_response(
            data=ScheduleList(
                id=updated_item.id,
                week_id=updated_item.week_id,
                lesson_time_id=updated_item.lesson_time_id,
                class_id=updated_item.class_id,
                class_name=updated_item.class_.name,
                teacher_id=updated_item.teacher_id,
                teacher_name=updated_item.teacher.user.full_name,
                subject_id=updated_item.subject_id,
                subject_name=updated_item.subject.name,
                day_of_week=updated_item.day_of_week,
                location=updated_item.location,
                description=updated_item.description,
                is_replacement=updated_item.is_replacement,
                is_cancelled=updated_item.is_cancelled,
                original_teacher_id=updated_item.original_teacher_id,
                original_teacher_name=updated_item.original_teacher.user.full_name if updated_item.original_teacher else None,
                lesson_num=updated_item.lesson_time.lesson_num,
                start_time=updated_item.lesson_time.start_time,
                end_time=updated_item.lesson_time.end_time,
                created_at=updated_item.created_at
            ),
            message="Элемент расписания успешно обновлен"
        )
    except Exception as e:
        logger.error(f"UPDATE_SCHEDULE_ITEM_ERROR: {e}")
        return error_response(
            message="Не удалось обновить элемент расписания",
            error_code="UPDATE_SCHEDULE_ITEM_ERROR"
        )

@router.delete("/{schedule_id}", response_model=Union[BaseResponse[dict], ErrorResponse])
async def delete_schedule_item(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить элемент расписания"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        schedule_item = await schedule_repository.get(db=db, id=schedule_id)
        if not schedule_item:
            return error_response(
                message="Элемент расписания не найден",
                error_code="SCHEDULE_ITEM_NOT_FOUND"
            )

        await schedule_repository.remove(db=db, id=schedule_id)

        return success_response(
            data={"deleted_id": schedule_id},
            message="Элемент расписания успешно удален"
        )
    except Exception as e:
        logger.error(f"DELETE_SCHEDULE_ITEM_ERROR: {e}")
        return error_response(
            message="Не удалось удалить элемент расписания",
            error_code="DELETE_SCHEDULE_ITEM_ERROR"
        )

# Homework endpoints
@router.get("/homework", response_model=Union[BaseResponse[List[HomeworkList]], ErrorResponse])
async def get_homework(
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    is_done: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить домашние задания"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Если это студент, он может видеть только свои задания
        if current_user.role == UserRole.STUDENT:
            student = await user_repository.get_user_student(db=db, user_id=current_user.id)
            if not student:
                return error_response(
                    message="Студент не найден",
                    error_code="STUDENT_NOT_FOUND"
                )
            student_id = student.user_id

        # Если это учитель, он может видеть только свои задания (если не указан student_id)
        if current_user.role == UserRole.TEACHER and not student_id:
            teacher_id = current_user.id

        if student_id:
            homework_items = await homework_repository.get_homework_by_student(
                db=db, student_id=student_id, skip=skip, limit=limit, is_done=is_done
            )
        elif teacher_id:
            homework_items = await homework_repository.get_homework_by_teacher(
                db=db, teacher_id=teacher_id, skip=skip, limit=limit
            )
        elif class_id and subject_id:
            homework_items = await homework_repository.get_homework_by_class_and_subject(
                db=db, class_id=class_id, subject_id=subject_id, skip=skip, limit=limit
            )
        else:
            return error_response(
                message="Необходимо указать student_id, teacher_id или class_id с subject_id",
                error_code="INVALID_PARAMETERS"
            )

        homework_list = []
        for item in homework_items:
            homework_list.append(HomeworkList(
                id=item.id,
                schedule_id=item.schedule_id,
                teacher_id=item.teacher_id,
                teacher_name=item.teacher.user.full_name,
                student_id=item.student_id,
                student_name=item.student.user.full_name,
                subject_id=item.subject_id,
                subject_name=item.subject.name,
                description=item.description,
                assignment_at=item.assignment_at,
                due_date=item.due_date,
                is_done=item.is_done,
                file_id=item.file_id,
                created_at=item.created_at
            ))

        return success_response(
            data=homework_list,
            message="Домашние задания успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_HOMEWORK_ERROR: {e}")
        return error_response(
            message="Не удалось получить домашние задания",
            error_code="GET_HOMEWORK_ERROR"
        )

@router.post("/homework", response_model=Union[BaseResponse[HomeworkList], ErrorResponse])
async def create_homework(
    homework_create: HomeworkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать домашнее задание"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Если это учитель, он может создавать только свои задания
        if current_user.role == UserRole.TEACHER:
            homework_create.teacher_id = current_user.id

        homework = await homework_repository.create(db=db, obj_in=homework_create)

        # Получаем созданное задание с связанными объектами
        created_homework = await homework_repository.get(db=db, id=homework.id)

        return success_response(
            data=HomeworkList(
                id=created_homework.id,
                schedule_id=created_homework.schedule_id,
                teacher_id=created_homework.teacher_id,
                teacher_name=created_homework.teacher.user.full_name,
                student_id=created_homework.student_id,
                student_name=created_homework.student.user.full_name,
                subject_id=created_homework.subject_id,
                subject_name=created_homework.subject.name,
                description=created_homework.description,
                assignment_at=created_homework.assignment_at,
                due_date=created_homework.due_date,
                is_done=created_homework.is_done,
                file_id=created_homework.file_id,
                created_at=created_homework.created_at
            ),
            message="Домашнее задание успешно создано"
        )
    except Exception as e:
        logger.error(f"CREATE_HOMEWORK_ERROR: {e}")
        return error_response(
            message="Не удалось создать домашнее задание",
            error_code="CREATE_HOMEWORK_ERROR"
        )

# Grades endpoints
@router.get("/grades", response_model=Union[BaseResponse[List[GradeList]], ErrorResponse])
async def get_grades(
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить оценки"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Если это студент, он может видеть только свои оценки
        if current_user.role == UserRole.STUDENT:
            student = await user_repository.get_user_student(db=db, user_id=current_user.id)
            if not student:
                return error_response(
                    message="Студент не найден",
                    error_code="STUDENT_NOT_FOUND"
                )
            student_id = student.user_id

        # Если это учитель, он может видеть только свои оценки (если не указан student_id)
        if current_user.role == UserRole.TEACHER and not student_id:
            teacher_id = current_user.id

        if student_id:
            grades = await grade_repository.get_grades_by_student(
                db=db, student_id=student_id, subject_id=subject_id, skip=skip, limit=limit
            )
        elif teacher_id:
            grades = await grade_repository.get_grades_by_teacher(
                db=db, teacher_id=teacher_id, class_id=class_id, subject_id=subject_id, skip=skip, limit=limit
            )
        elif class_id and subject_id:
            grades = await grade_repository.get_grades_by_class_and_subject(
                db=db, class_id=class_id, subject_id=subject_id, skip=skip, limit=limit
            )
        else:
            return error_response(
                message="Необходимо указать student_id, teacher_id или class_id с subject_id",
                error_code="INVALID_PARAMETERS"
            )

        grades_list = []
        for grade in grades:
            grades_list.append(GradeList(
                id=grade.id,
                schedule_id=grade.schedule_id,
                student_id=grade.student_id,
                student_name=grade.student.user.full_name,
                subject_id=grade.subject_id,
                subject_name=grade.subject.name,
                teacher_id=grade.teacher_id,
                teacher_name=grade.teacher.user.full_name,
                homework_id=grade.homework_id,
                comment=grade.comment,
                score=grade.score,
                created_at=grade.created_at
            ))

        return success_response(
            data=grades_list,
            message="Оценки успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_GRADES_ERROR: {e}")
        return error_response(
            message="Не удалось получить оценки",
            error_code="GET_GRADES_ERROR"
        )

@router.post("/grades", response_model=Union[BaseResponse[GradeList], ErrorResponse])
async def create_grade(
    grade_create: GradeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать оценку"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Если это учитель, он может создавать только свои оценки
        if current_user.role == UserRole.TEACHER:
            grade_create.teacher_id = current_user.id

        grade = await grade_repository.create(db=db, obj_in=grade_create)

        # Получаем созданную оценку с связанными объектами
        created_grade = await grade_repository.get(db=db, id=grade.id)

        return success_response(
            data=GradeList(
                id=created_grade.id,
                schedule_id=created_grade.schedule_id,
                student_id=created_grade.student_id,
                student_name=created_grade.student.user.full_name,
                subject_id=created_grade.subject_id,
                subject_name=created_grade.subject.name,
                teacher_id=created_grade.teacher_id,
                teacher_name=created_grade.teacher.user.full_name,
                homework_id=created_grade.homework_id,
                comment=created_grade.comment,
                score=created_grade.score,
                created_at=created_grade.created_at
            ),
            message="Оценка успешно создана"
        )
    except Exception as e:
        logger.error(f"CREATE_GRADE_ERROR: {e}")
        return error_response(
            message="Не удалось создать оценку",
            error_code="CREATE_GRADE_ERROR"
        ) 