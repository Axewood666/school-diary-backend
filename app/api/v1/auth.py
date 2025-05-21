from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.auth import Token, User, UserCreate, UserInvite, UserInviteCreate, UserRole, AcceptInvite, UserInviteInfo
from app.services.auth import authenticate_user, create_user, create_user_token, create_user_invite, invite_accept_process
from app.services.mailer import get_mailer_service, MailerService
from app.db.repositories.user import user_repository
from app.db.repositories.user_invites import user_invite_repository
from typing import List

from datetime import datetime
router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = await authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_user_token(user_id=str(user.id))


@router.post("/invite")
async def invite_user(
    user_invite: UserInviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mailer_service: MailerService = Depends(get_mailer_service)
):
    """Invite a user to the system"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to invite users",
        )
    invite = await create_user_invite(db=db, user_invite_in=user_invite, mailer_service=mailer_service)
    return {"message": f"{user_invite.full_name} успешно приглашен. Срок действия ссылки: {invite.expires_at}"}


@router.post("/invite/accept", response_model=Token)
async def accept_invite(accept_invite: AcceptInvite, db: AsyncSession = Depends(get_db)):
    """Accept invite"""
    credentials = await invite_accept_process(accept_invite=accept_invite, db=db)
    return credentials
    
    
@router.get("/invite/list", response_model=List[UserInviteInfo])
async def get_invites(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all invites"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to get invites",
        )
    invites = await user_invite_repository.get_multi(db=db, skip=skip, limit=limit)
    invites_list = [UserInviteInfo(
        role=invite.role,
        full_name=invite.full_name,
        email=invite.email,
        created_at=invite.created_at,
        expires_at=invite.expires_at,
        is_sent=invite.is_sent,
        used_at=invite.used_at) for invite in invites]
    return invites_list


@router.get("/invite/{token}", response_model=bool)
async def get_invite(token: str, db: AsyncSession = Depends(get_db)):
    """Check validity of invite"""
    invite = await user_invite_repository.get_by_token(db=db, token=token)
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
    return True

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user 