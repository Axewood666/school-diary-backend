from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.role import User, UserRole, UserResponse, UserStudent, UserTeacher, Student, Teacher
from app.schemas.response import (
    success_response, error_response, ErrorResponse,
    UserInfoSuccessResponse, UsersListSuccessResponse, StudentsListSuccessResponse,
    StudentInfoSuccessResponse, TeachersListSuccessResponse, TeacherInfoSuccessResponse,
    AdminsListSuccessResponse, UserUpdateSuccessResponse
)
from app.db.repositories.user import user_repository
from typing import List

router = APIRouter(tags=["users"])

@router.get("/me", response_model=Union[UserInfoSuccessResponse, ErrorResponse])
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

@router.get("/", response_model=Union[UsersListSuccessResponse, ErrorResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        users = await user_repository.get_all(db=db)
        
        return success_response(
            data={
                "users": users[skip:skip+limit],
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(users)
                }
            },
            message="Users retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve users",
            error_code="GET_USERS_ERROR"
        )

@router.get("/{user_id}", response_model=Union[UserInfoSuccessResponse, ErrorResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user information"""
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
        return error_response(
            message="Failed to retrieve user",
            error_code="GET_USER_ERROR"
        )

@router.get("/students", response_model=Union[StudentsListSuccessResponse, ErrorResponse])
async def get_user_students(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all students"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        students = await user_repository.get_all_students(db=db)
        students_data = []
        
        for student in students[skip:skip+limit]:
            students_data.append({
                "user": {
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
                "students": students_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(students)
                }
            },
            message="Students retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve students",
            error_code="GET_STUDENTS_ERROR"
        )

@router.get("/students/{user_id}", response_model=Union[StudentInfoSuccessResponse, ErrorResponse])
async def get_user_student(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user student"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        student = await user_repository.get_user_student(db=db, user_id=user_id)
        if not student:
            return error_response(
                message="User student not found",
                error_code="STUDENT_NOT_FOUND"
            )
        
        student_data = {
            "user": {
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
        return error_response(
            message="Failed to retrieve student",
            error_code="GET_STUDENT_ERROR"
        )

@router.get("/teachers", response_model=Union[TeachersListSuccessResponse, ErrorResponse])
async def get_user_teachers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all teachers"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        teachers = await user_repository.get_all_teachers(db=db)
        teachers_data = []
        
        for teacher in teachers[skip:skip+limit]:
            teachers_data.append({
                "user": {
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
                "teachers": teachers_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(teachers)
                }
            },
            message="Teachers retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve teachers",
            error_code="GET_TEACHERS_ERROR"
        )

@router.get("/teachers/{user_id}", response_model=Union[TeacherInfoSuccessResponse, ErrorResponse])
async def get_user_teacher(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user teacher"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        teacher = await user_repository.get_user_teacher(db=db, user_id=user_id)
        if not teacher:
            return error_response(
                message="User teacher not found",
                error_code="TEACHER_NOT_FOUND"
            )
        
        teacher_data = {
            "user": {
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
        return error_response(
            message="Failed to retrieve teacher",
            error_code="GET_TEACHER_ERROR"
        )

@router.get("/admins/{user_id}", response_model=Union[AdminsListSuccessResponse, ErrorResponse])
async def get_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user admin"""
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
        
        return success_response(
            data=admin,
            message="Admin retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve admin",
            error_code="GET_ADMIN_ERROR"
        )

@router.get("/admins", response_model=Union[AdminsListSuccessResponse, ErrorResponse])
async def get_user_admins(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all admins"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        admins = await user_repository.get_all_admins(db=db)
        
        return success_response(
            data={
                "admins": admins[skip:skip+limit],
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(admins)
                }
            },
            message="Admins retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve admins",
            error_code="GET_ADMINS_ERROR"
        )

@router.patch("/{user_id}", response_model=Union[UserUpdateSuccessResponse, ErrorResponse])
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate user"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        is_deactivated = await user_repository.deactivate_user(db=db, user_id=user_id)
        if not is_deactivated:
            return error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        return success_response(
            data={"is_deactivated": True},
            message="User deactivated successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to deactivate user",
            error_code="DEACTIVATE_USER_ERROR"
        )
