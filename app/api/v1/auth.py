from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.auth import Token, UserInviteRequest, UserInviteCreate, UserRole, AcceptInvite, UserInviteInfo
from app.schemas.role import User
from app.schemas.response import (
    success_response, error_response, ErrorResponse,
    LoginSuccessResponse, InviteSuccessResponse, InviteAcceptSuccessResponse,
    InviteListSuccessResponse, InviteValidationSuccessResponse
)
from app.services.auth import authenticate_user, create_user, create_user_token, create_user_invite, invite_accept_process
from app.services.mailer import get_mailer_service, MailerService
from app.db.repositories.user import user_repository
from app.db.repositories.user_invites import user_invite_repository
from typing import List

from datetime import datetime
router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Union[LoginSuccessResponse, ErrorResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    try:
        user = await authenticate_user(db=db, username=form_data.username, password=form_data.password)
        if not user or not user.is_active:
            return error_response(
                message="Incorrect username or password",
                error_code="INVALID_CREDENTIALS"
            )
        
        token_data = create_user_token(user_id=str(user.id))
        return success_response(
            data=token_data,
            message="Login successful"
        )
    except Exception as e:
        return error_response(
            message="Login failed",
            error_code="LOGIN_ERROR"
        )


@router.post("/invite", response_model=Union[InviteSuccessResponse, ErrorResponse])
async def invite_user(
    user_invite: UserInviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mailer_service: MailerService = Depends(get_mailer_service)
):
    """Invite a user to the system"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to invite users",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        invite = await create_user_invite(db=db, user_invite_in=user_invite, mailer_service=mailer_service)
        return success_response(
            data=invite,
            message="User invited successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to invite user",
            error_code="INVITE_ERROR"
        )


@router.post("/invite/accept", response_model=Union[InviteAcceptSuccessResponse, ErrorResponse])
async def accept_invite(accept_invite: AcceptInvite, db: AsyncSession = Depends(get_db)):
    """Accept invite"""
    try:
        credentials = await invite_accept_process(accept_invite=accept_invite, db=db)
        return success_response(
            data=credentials,
            message="Invite accepted successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to accept invite",
            error_code="INVITE_ACCEPT_ERROR"
        )
    
    
@router.get("/invite/list", response_model=Union[InviteListSuccessResponse, ErrorResponse])
async def get_invites(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all invites"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to get invites",
                error_code="INSUFFICIENT_PERMISSIONS"
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
        
        return success_response(
            data={
                "invites": invites_list,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": len(invites_list)
                }
            },
            message="Invites retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve invites",
            error_code="GET_INVITES_ERROR"
        )


@router.get("/invite/{token}", response_model=Union[InviteValidationSuccessResponse, ErrorResponse])
async def is_valid_invite(token: str, db: AsyncSession = Depends(get_db)):
    """Check validity of invite"""
    try:
        invite = await user_invite_repository.get_by_token(db=db, token=token)
        if not invite:
            return error_response(
                message="Invite not found",
                error_code="INVITE_NOT_FOUND"
            )
        
        if invite.is_expired():
            return error_response(
                message="Invite expired",
                error_code="INVITE_EXPIRED"
            )
        
        if invite.is_used():
            return error_response(
                message="Invite already used",
                error_code="INVITE_ALREADY_USED"
            )
        
        return success_response(
            data={
                "is_valid": True,
                "invite_info": {
                    "email": invite.email,
                    "full_name": invite.full_name,
                    "role": invite.role,
                    "expires_at": invite.expires_at,
                    "created_at": invite.created_at
                }
            },
            message="Invite is valid"
        )
    except Exception as e:
        return error_response(
            message="Failed to validate invite",
            error_code="INVITE_VALIDATION_ERROR"
        )