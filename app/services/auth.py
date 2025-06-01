from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.repositories.user.user import user_repository
from app.db.repositories.user.student import student_repository
from app.db.repositories.user.teacher import teacher_repository
from app.schemas.auth.auth import Token, UserInviteCreate, AcceptInvite
from app.services.mailer import MailerService
from datetime import datetime
from app.services.helpers import username_from_fio
from app.schemas.user.student import StudentInDb
from app.schemas.user.teacher import TeacherInDb
from app.schemas.user.user import UserInDB, UserCreate
from app.db.models.user import UserRole
from app.db.repositories.auth.user_invites import user_invite_repository

async def get_user_by_id(db: AsyncSession, user_id: int):
    return await user_repository.get(db=db, id=user_id)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await user_repository.get_by_username(db=db, username=username)
    if not user:
        user = await user_repository.get_by_email(db=db, email=username)
        if not user:
            return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


async def create_user(db: AsyncSession, user_in: UserCreate):
    existing_user = await user_repository.get_by_email(db=db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    existing_username = await user_repository.get_by_username(db=db, username=user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    db_user = await user_repository.create(db=db, obj_in=UserInDB(**user_data))
    return db_user


def create_user_token(user_id: str) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer") 

async def create_user_invite(db: AsyncSession, 
                                user_invite_in: UserInviteCreate, 
                                mailer_service: MailerService):
    """Создает приглашение для пользователя и отправляет его на email(пока синхронно)"""
    user=await user_repository.get_by_email(db=db, email=user_invite_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
        
    user_invite = await user_invite_repository.get_by_email(db=db, email=user_invite_in.email)
    if user_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already invited",
        )
        
    user_invite = await user_invite_repository.create_user_invite(db=db, obj_in=user_invite_in)
    
    # TODO: Отправка асинхронной почты
    result_status = await mailer_service.send_email(user_invite.email, "Приглашение в систему", f"Приглашение в систему: {settings.FRONTEND_URL}/invite?token={user_invite.token}")
    
    if result_status:
        await user_invite_repository.update_sent_status(db=db, user_invite_id=user_invite.id)
        return user_invite
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )
        
async def invite_accept_process(accept_invite: AcceptInvite, db: AsyncSession) -> int:
    """
    Если произойдет ошибка при создании профиля (student/teacher), 
    откатывается создание пользователя и обновление приглашения.
    """
    async with db.begin() as transaction:
        try:
            invite = await user_invite_repository.get_by_token(db=db, token=accept_invite.token)
            if not invite:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invite not found",
                )
                
            if invite.is_expired():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invite expired",
                )
            
            if invite.is_used():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invite already used",
                )
            
            user = await user_repository.get_by_email(db=db, email=invite.email)
            if user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists",
                )
            
            savepoint = await db.begin_nested()
            
            try:
                hashed_password = get_password_hash(accept_invite.password)
                username = username_from_fio(invite.full_name)
                user_data = {
                    "email": invite.email,
                    "username": username,
                    "hashed_password": hashed_password,
                    "full_name": invite.full_name,
                    "role": invite.role
                }
                db_user = await user_repository.create_without_commit(db=db, obj_in=UserInDB(**user_data))
                
                invite.used_at = datetime.now()
                await user_invite_repository.update_used_status(db=db, user_invite_id=invite.id)
                
                if invite.role == UserRole.STUDENT:
                    student_data = {
                        "user_id": db_user.id,
                        "class_id": None,
                        "parent_phone": None,
                        "parent_email": None,
                        "parent_fio": None
                    }
                    await student_repository.create_student(db=db, student_in=StudentInDb(**student_data))
                    
                elif invite.role == UserRole.TEACHER:
                    teacher_data = {
                        "user_id": db_user.id,
                        "class_id": None,
                        "degree": None,
                        "experience": None,
                        "bio": None
                    }
                    await teacher_repository.create_teacher(db=db, teacher_in=TeacherInDb(**teacher_data))
                
                await savepoint.commit()
                
                return db_user.id
                
            except Exception as profile_error:
                await savepoint.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user profile: {str(profile_error)}",
                )
                
        except HTTPException:
            raise
        except Exception as e:
            await transaction.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transaction failed: {str(e)}",
            )
