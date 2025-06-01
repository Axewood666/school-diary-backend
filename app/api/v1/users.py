from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.core.dependencies import get_current_user
from app.db.session import get_db

from app.schemas.base import success_response, error_response, ErrorResponse, BaseResponse
from app.schemas.responses import TeachersListData, UserWithTeacherInfo, AdminsListData, UsersListData, StudentsListData, UserWithStudentInfo
from app.schemas.user.user import User, UserRole, UserDeactivateData, UserResponse


from app.db.repositories.user.user import user_repository
from app.db.repositories.user.student import student_repository
from app.db.repositories.user.teacher import teacher_repository
import logging
from app.core.logger import setup_logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["users"])

@router.get("/me", response_model=Union[BaseResponse[User], ErrorResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    try:
        return success_response(
            data=current_user,
            message="Current user information retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve current user information",
            error_code="GET_CURRENT_USER_ERROR"
        )

@router.get("/students", response_model=Union[BaseResponse[StudentsListData], ErrorResponse])
async def get_user_students(
    skip: int = 0,
    limit: int = 100,
    class_id: int = None,
    teacher_id: int = None,
    search: str = None,
    order_by: str = "created_at",
    order_direction: str = "desc",
    is_active: bool = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка студентов с фильтрацией и пагинацией.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role == UserRole.TEACHER:
            teacher_id = current_user.id
        elif current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        students = await student_repository.get_students(
            db=db, 
            teacher_id=teacher_id,
            class_id=class_id, 
            search=search, 
            order_by=order_by, 
            order_direction=order_direction, 
            is_active=is_active,
            skip=skip,
            limit=limit
        )
            
        students_data = []
        for student in students:
            students_data.append({
                "user_info": {
                    "id": student.user.id,
                    "email": student.user.email,
                    "username": student.user.username,
                    "full_name": student.user.full_name,
                    "is_active": student.user.is_active,
                    "role": student.user.role
                },
                "student_info": {
                    "class_id": student.class_id,
                    "parent_phone": student.parent_phone,
                    "parent_email": student.parent_email,
                    "parent_fio": student.parent_fio
                }
            })
        
        return success_response(
            data={
                "items": students_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(students)
                }
            },
            message="Students retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_STUDENTS_ERROR: {e}")
        return error_response(
            message="Failed to retrieve students",
            error_code="GET_STUDENTS_ERROR"
        )

@router.get("/students/{user_id}", response_model=Union[BaseResponse[UserWithStudentInfo], ErrorResponse])
async def get_user_student(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о конкретном студенте.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        student = await student_repository.get_user_student(db=db, user_id=user_id)
        if not student:
            return error_response(
                message="User student not found",
                error_code="STUDENT_NOT_FOUND"
            )

        if current_user.role == UserRole.ADMIN:
            pass
        elif current_user.role == UserRole.STUDENT:
            if current_user.id != user_id:
                return error_response(
                    message="You are not allowed to access this resource",
                    error_code="INSUFFICIENT_PERMISSIONS"
                )
        elif current_user.role == UserRole.TEACHER:
            teacher = await teacher_repository.get_user_teacher(db=db, user_id=current_user.id)
            
            is_class_teacher = teacher.class_id == student.class_id
            
            has_lessons = False
            if student.class_id:
                has_lessons = await teacher_repository.is_class_teacher(db=db, user_id=current_user.id, class_id=student.class_id)
                
            if not (is_class_teacher or has_lessons):
                return error_response(
                    message="You are not allowed to access this resource",
                    error_code="INSUFFICIENT_PERMISSIONS"
                )
        else:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        student_data = {
            "user_info": {
                "id": student.user.id,
                "email": student.user.email,
                "username": student.user.username,
                "full_name": student.user.full_name,
                "is_active": student.user.is_active,
                "role": student.user.role
            },
            "student_info": {
                "class_id": student.class_id,
                "parent_phone": student.parent_phone,
                "parent_email": student.parent_email,
                "parent_fio": student.parent_fio
            }
        }
        
        return success_response(
            data=student_data,
            message="Student retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_STUDENT_ERROR: {e}")
        return error_response(
            message="Failed to retrieve student",
            error_code="GET_STUDENT_ERROR"
        )

@router.get("/teachers", response_model=Union[BaseResponse[TeachersListData], ErrorResponse])
async def get_user_teachers(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    order_by: str = "created_at",
    order_direction: str = "desc",
    is_active: bool = None,
    class_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка учителей с фильтрацией и пагинацией.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        teachers = await teacher_repository.get_teachers(
            db=db, 
            search=search, 
            order_by=order_by, 
            order_direction=order_direction, 
            is_active=is_active,
            class_id=class_id,
            skip=skip,
            limit=limit
        )
        
        teachers_data = []
        for teacher in teachers:
            teachers_data.append({
                "user_info": {
                    "id": teacher.user.id,
                    "email": teacher.user.email,
                    "username": teacher.user.username,
                    "full_name": teacher.user.full_name,
                    "is_active": teacher.user.is_active,
                    "role": teacher.user.role
                },
                "teacher_info": {
                    "class_id": teacher.class_id,
                    "degree": teacher.degree,
                    "experience": teacher.experience,
                    "bio": teacher.bio
                }
            })
        
        return success_response(
            data={
                "items": teachers_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(teachers)
                }
            },
            message="Teachers retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_TEACHERS_ERROR: {e}")
        return error_response(
            message="Failed to retrieve teachers",
            error_code="GET_TEACHERS_ERROR"
        )

@router.get("/teachers/{user_id}", response_model=Union[BaseResponse[UserWithTeacherInfo], ErrorResponse])
async def get_user_teacher(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о конкретном учителе.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        teacher = await teacher_repository.get_user_teacher(db=db, user_id=user_id)
        if not teacher:
            return error_response(
                message="User teacher not found",
                error_code="TEACHER_NOT_FOUND"
            )

        if current_user.role == UserRole.ADMIN:
            pass
        elif current_user.role == UserRole.TEACHER:
            if current_user.id != user_id:
                return error_response(
                    message="You are not allowed to access this resource",
                    error_code="INSUFFICIENT_PERMISSIONS"
                )
        else:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        teacher_data = {
            "user_info": {
                "id": teacher.user.id,
                "email": teacher.user.email,
                "username": teacher.user.username,
                "full_name": teacher.user.full_name,
                "is_active": teacher.user.is_active,
                "role": teacher.user.role
            },
            "teacher_info": {
                "class_id": teacher.class_id,
                "degree": teacher.degree,
                "experience": teacher.experience,
                "bio": teacher.bio
            }
        }
        
        return success_response(
            data=teacher_data,
            message="Teacher retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_TEACHER_ERROR: {e}")
        return error_response(
            message="Failed to retrieve teacher",
            error_code="GET_TEACHER_ERROR"
        )

@router.get("/admins", response_model=Union[BaseResponse[AdminsListData], ErrorResponse])
async def get_user_admins(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    search: str = None,
    order_by: str = "created_at",
    order_direction: str = "desc",
    is_active: bool = None
):
    """
    Получение списка администраторов с фильтрацией и пагинацией.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        admins = await user_repository.get_users(
            db=db, 
            skip=skip, 
            limit=limit, 
            search=search, 
            order_by=order_by, 
            order_direction=order_direction, 
            is_active=is_active, 
            role=UserRole.ADMIN
        )
        
        admins_data = []
        for admin in admins:
            admins_data.append({
                "id": admin.id,
                "email": admin.email,
                "username": admin.username,
                "full_name": admin.full_name,
                "is_active": admin.is_active,
                "role": admin.role
            })
        
        return success_response(
            data={
                "items": admins_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(admins)
                }
            },
            message="Admins retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_ADMINS_ERROR: {e}")
        return error_response(
            message="Failed to retrieve admins",
            error_code="GET_ADMINS_ERROR"
        )

@router.get("/admins/{user_id}", response_model=Union[BaseResponse[UserResponse], ErrorResponse])
async def get_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о конкретном администраторе.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        admin = await user_repository.get_user_admin(db=db, user_id=user_id)
        if not admin:
            return error_response(
                message="User admin not found",
                error_code="ADMIN_NOT_FOUND"
            )
        
        admin_data = {
            "id": admin.id,
            "email": admin.email,
            "username": admin.username,
            "full_name": admin.full_name,
            "is_active": admin.is_active,
            "role": admin.role
        }
        
        return success_response(
            data=admin_data,
            message="Admin retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_ADMIN_ERROR: {e}")
        return error_response(
            message="Failed to retrieve admin",
            error_code="GET_ADMIN_ERROR"
        )

@router.get("/", response_model=Union[BaseResponse[UsersListData], ErrorResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    search: str = None,
    order_by: str = "created_at",
    order_direction: str = "desc",
    is_active: bool = None,
    role: UserRole = None
):
    """
    Получение списка всех пользователей с фильтрацией и пагинацией.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        users = await user_repository.get_users(
            db=db, 
            skip=skip, 
            limit=limit, 
            search=search, 
            order_by=order_by, 
            order_direction=order_direction, 
            is_active=is_active, 
            role=role
        )
        
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "role": user.role
            })
        
        return success_response(
            data={
                "items": users_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(users)
                }
            },
            message="Users retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_USERS_ERROR: {e}")
        return error_response(
            message="Failed to retrieve users",
            error_code="GET_USERS_ERROR"
        )

@router.get("/{user_id}", response_model=Union[BaseResponse[User], ErrorResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о конкретном пользователе.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        user = await user_repository.get(db=db, id=user_id)
        if not user:
            return error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        return success_response(
            data=user,
            message="User retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_USER_ERROR: {e}")
        return error_response(
            message="Failed to retrieve user",
            error_code="GET_USER_ERROR"
        )

@router.patch("/{user_id}", response_model=Union[BaseResponse[UserDeactivateData], ErrorResponse])
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Деактивация пользователя в системе.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        user = await user_repository.deactivate_user(db=db, user_id=user_id)
        if not user:
            return error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        return success_response(
            data=UserDeactivateData(
                id=user.id,
                is_active=user.is_active
            ),
            message="User deactivated successfully"
        )
    except ValueError as e:
        logger.error(f"VALIDATION_ERROR: {e}")
        return error_response(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )
    except Exception as e:
        logger.error(f"DEACTIVATE_USER_ERROR: {e}")
        return error_response(
            message="Failed to deactivate user",
            error_code="DEACTIVATE_USER_ERROR"
        )

