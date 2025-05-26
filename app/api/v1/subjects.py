from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Optional

from app.schemas.base import error_response, BaseResponse, ErrorResponse, success_response
from app.schemas.user import UserRole, User
from app.schemas.subject import (
    SubjectCreate, SubjectUpdate, SubjectList, SubjectWithTeachers,
    TeacherSubjectCreate, TeacherSubjectUpdate, TeacherSubjectList
)

from app.core.dependencies import get_db, get_current_user
from app.core.logger import setup_logging
from app.db.repositories.subject import subject_repository, teacher_subject_repository
from app.db.repositories.user import user_repository

import logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["subjects"])

@router.get("/", response_model=Union[BaseResponse[List[SubjectList]], ErrorResponse])
async def get_subjects(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    order_by: str = "created_at",
    order_direction: str = "desc",
    with_teachers: bool = False,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Получить список предметов"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        if with_teachers:
            subjects = await subject_repository.get_subjects_with_teachers(
                db=db, skip=skip, limit=limit, search=search
            )
            subject_list = []
            for subject in subjects:
                teachers = []
                for ts in subject.teacher_subjects:
                    teachers.append(TeacherSubjectList(
                        id=ts.id,
                        teacher_id=ts.teacher_id,
                        subject_id=ts.subject_id,
                        subject_name=subject.name,
                        is_main=ts.is_main,
                        created_at=ts.created_at
                    ))
                
                subject_list.append(SubjectWithTeachers(
                    id=subject.id,
                    name=subject.name,
                    back_ground_color=subject.back_ground_color,
                    border_color=subject.border_color,
                    text_color=subject.text_color,
                    icon=subject.icon,
                    created_at=subject.created_at,
                    teachers=teachers
                ))
        else:
            subjects = await subject_repository.get_subjects(
                db=db, skip=skip, limit=limit, search=search, 
                order_by=order_by, order_direction=order_direction
            )
            subject_list = [
                SubjectList(
                    id=subject.id,
                    name=subject.name,
                    back_ground_color=subject.back_ground_color,
                    border_color=subject.border_color,
                    text_color=subject.text_color,
                    icon=subject.icon,
                    created_at=subject.created_at
                ) for subject in subjects
            ]

        return success_response(
            data=subject_list,
            message="Предметы успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_SUBJECTS_ERROR: {e}")
        return error_response(
            message="Не удалось получить предметы",
            error_code="GET_SUBJECTS_ERROR"
        )

@router.post("/", response_model=Union[BaseResponse[SubjectList], ErrorResponse])
async def create_subject(
    subject_create: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый предмет"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        subject = await subject_repository.create(db=db, obj_in=subject_create)
        
        return success_response(
            data=SubjectList(
                id=subject.id,
                name=subject.name,
                back_ground_color=subject.back_ground_color,
                border_color=subject.border_color,
                text_color=subject.text_color,
                icon=subject.icon,
                created_at=subject.created_at
            ),
            message="Предмет успешно создан"
        )
    except Exception as e:
        logger.error(f"CREATE_SUBJECT_ERROR: {e}")
        return error_response(
            message="Не удалось создать предмет",
            error_code="CREATE_SUBJECT_ERROR"
        )

@router.get("/{subject_id}", response_model=Union[BaseResponse[SubjectList], ErrorResponse])
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить предмет по ID"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        subject = await subject_repository.get(db=db, id=subject_id)
        if not subject:
            return error_response(
                message="Предмет не найден",
                error_code="SUBJECT_NOT_FOUND"
            )

        return success_response(
            data=SubjectList(
                id=subject.id,
                name=subject.name,
                back_ground_color=subject.back_ground_color,
                border_color=subject.border_color,
                text_color=subject.text_color,
                icon=subject.icon,
                created_at=subject.created_at
            ),
            message="Предмет успешно получен"
        )
    except Exception as e:
        logger.error(f"GET_SUBJECT_ERROR: {e}")
        return error_response(
            message="Не удалось получить предмет",
            error_code="GET_SUBJECT_ERROR"
        )

@router.patch("/{subject_id}", response_model=Union[BaseResponse[SubjectList], ErrorResponse])
async def update_subject(
    subject_id: int,
    subject_update: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить предмет"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        subject = await subject_repository.get(db=db, id=subject_id)
        if not subject:
            return error_response(
                message="Предмет не найден",
                error_code="SUBJECT_NOT_FOUND"
            )

        subject = await subject_repository.update(db=db, db_obj=subject, obj_in=subject_update)

        return success_response(
            data=SubjectList(
                id=subject.id,
                name=subject.name,
                back_ground_color=subject.back_ground_color,
                border_color=subject.border_color,
                text_color=subject.text_color,
                icon=subject.icon,
                created_at=subject.created_at
            ),
            message="Предмет успешно обновлен"
        )
    except Exception as e:
        logger.error(f"UPDATE_SUBJECT_ERROR: {e}")
        return error_response(
            message="Не удалось обновить предмет",
            error_code="UPDATE_SUBJECT_ERROR"
        )

@router.delete("/{subject_id}", response_model=Union[BaseResponse[dict], ErrorResponse])
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить предмет"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        subject = await subject_repository.get(db=db, id=subject_id)
        if not subject:
            return error_response(
                message="Предмет не найден",
                error_code="SUBJECT_NOT_FOUND"
            )

        await subject_repository.remove(db=db, id=subject_id)

        return success_response(
            data={"deleted_id": subject_id},
            message="Предмет успешно удален"
        )
    except Exception as e:
        logger.error(f"DELETE_SUBJECT_ERROR: {e}")
        return error_response(
            message="Не удалось удалить предмет",
            error_code="DELETE_SUBJECT_ERROR"
        )

# Teacher-Subject endpoints
@router.post("/{subject_id}/teachers", response_model=Union[BaseResponse[TeacherSubjectList], ErrorResponse])
async def assign_teacher_to_subject(
    subject_id: int,
    teacher_id: int,
    is_main: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Назначить учителя на предмет"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Проверяем существование предмета
        subject = await subject_repository.get(db=db, id=subject_id)
        if not subject:
            return error_response(
                message="Предмет не найден",
                error_code="SUBJECT_NOT_FOUND"
            )

        # Проверяем существование учителя
        teacher = await user_repository.get_user_teacher(db=db, user_id=teacher_id)
        if not teacher:
            return error_response(
                message="Учитель не найден",
                error_code="TEACHER_NOT_FOUND"
            )

        # Проверяем, не назначен ли уже учитель на этот предмет
        existing = await teacher_subject_repository.get_by_teacher_and_subject(
            db=db, teacher_id=teacher_id, subject_id=subject_id
        )
        if existing:
            return error_response(
                message="Учитель уже назначен на этот предмет",
                error_code="TEACHER_ALREADY_ASSIGNED"
            )

        teacher_subject = await teacher_subject_repository.create(
            db=db, 
            obj_in=TeacherSubjectCreate(
                teacher_id=teacher_id,
                subject_id=subject_id,
                is_main=is_main
            )
        )

        return success_response(
            data=TeacherSubjectList(
                id=teacher_subject.id,
                teacher_id=teacher_subject.teacher_id,
                subject_id=teacher_subject.subject_id,
                subject_name=subject.name,
                is_main=teacher_subject.is_main,
                created_at=teacher_subject.created_at
            ),
            message="Учитель успешно назначен на предмет"
        )
    except Exception as e:
        logger.error(f"ASSIGN_TEACHER_TO_SUBJECT_ERROR: {e}")
        return error_response(
            message="Не удалось назначить учителя на предмет",
            error_code="ASSIGN_TEACHER_TO_SUBJECT_ERROR"
        )

@router.delete("/{subject_id}/teachers/{teacher_id}", response_model=Union[BaseResponse[dict], ErrorResponse])
async def remove_teacher_from_subject(
    subject_id: int,
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Убрать учителя с предмета"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        teacher_subject = await teacher_subject_repository.get_by_teacher_and_subject(
            db=db, teacher_id=teacher_id, subject_id=subject_id
        )
        if not teacher_subject:
            return error_response(
                message="Назначение не найдено",
                error_code="TEACHER_SUBJECT_NOT_FOUND"
            )

        await teacher_subject_repository.remove(db=db, id=teacher_subject.id)

        return success_response(
            data={"removed_teacher_id": teacher_id, "subject_id": subject_id},
            message="Учитель успешно убран с предмета"
        )
    except Exception as e:
        logger.error(f"REMOVE_TEACHER_FROM_SUBJECT_ERROR: {e}")
        return error_response(
            message="Не удалось убрать учителя с предмета",
            error_code="REMOVE_TEACHER_FROM_SUBJECT_ERROR"
        )

@router.get("/teacher/{teacher_id}", response_model=Union[BaseResponse[List[SubjectList]], ErrorResponse])
async def get_teacher_subjects(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить предметы учителя"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Если это учитель, он может видеть только свои предметы
        if current_user.role == UserRole.TEACHER and current_user.id != teacher_id:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        subjects = await subject_repository.get_teacher_subjects(db=db, teacher_id=teacher_id)
        
        subject_list = [
            SubjectList(
                id=subject.id,
                name=subject.name,
                back_ground_color=subject.back_ground_color,
                border_color=subject.border_color,
                text_color=subject.text_color,
                icon=subject.icon,
                created_at=subject.created_at
            ) for subject in subjects
        ]

        return success_response(
            data=subject_list,
            message="Предметы учителя успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_TEACHER_SUBJECTS_ERROR: {e}")
        return error_response(
            message="Не удалось получить предметы учителя",
            error_code="GET_TEACHER_SUBJECTS_ERROR"
        ) 