from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any, List
from app.schemas.auth import Token, UserInviteInfo
from app.schemas.role import User
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    result: bool
    response: Optional[T] = None
    message: Optional[str] = None

class SuccessResponse(BaseResponse[T]):
    result: bool = True

class ErrorResponse(BaseModel):
    result: bool = False
    message: str
    error_code: Optional[str] = None


class LoginSuccessResponse(BaseModel):
    result: bool = True
    response: Token
    message: str

class InviteSuccessResponse(BaseModel):
    result: bool = True
    response: dict  
    message: str

class InviteAcceptSuccessResponse(BaseModel):
    result: bool = True
    response: Token 
    message: str

class PaginationInfo(BaseModel):
    skip: int
    limit: int
    total: int

class InviteListData(BaseModel):
    invites: List[UserInviteInfo]
    pagination: PaginationInfo

class InviteListSuccessResponse(BaseModel):
    result: bool = True
    response: InviteListData
    message: str

class InviteValidationData(BaseModel):
    is_valid: bool
    invite_info: dict

class InviteValidationSuccessResponse(BaseModel):
    result: bool = True
    response: InviteValidationData
    message: str

class UserInfoSuccessResponse(BaseModel):
    result: bool = True
    response: User
    message: str

class UsersListData(BaseModel):
    users: List[User]
    pagination: PaginationInfo

class UsersListSuccessResponse(BaseModel):
    result: bool = True
    response: UsersListData
    message: str

class StudentsListData(BaseModel):
    students: List[dict]  
    pagination: PaginationInfo

class StudentsListSuccessResponse(BaseModel):
    result: bool = True
    response: StudentsListData
    message: str

class StudentInfoSuccessResponse(BaseModel):
    result: bool = True
    response: dict 
    message: str

class TeachersListData(BaseModel):
    teachers: List[dict] 
    pagination: PaginationInfo

class TeachersListSuccessResponse(BaseModel):
    result: bool = True
    response: TeachersListData
    message: str

class TeacherInfoSuccessResponse(BaseModel):
    result: bool = True
    response: dict  
    message: str

class AdminsListData(BaseModel):
    admins: List[User]
    pagination: PaginationInfo

class AdminsListSuccessResponse(BaseModel):
    result: bool = True
    response: AdminsListData
    message: str

class UserUpdateSuccessResponse(BaseModel):
    result: bool = True
    response: dict  
    message: str

def success_response(data: Any, message: str = "Success") -> dict:
    return {
        "result": True,
        "response": data,
        "message": message
    }

def error_response(message: str, error_code: Optional[str] = None) -> dict:
    return {
        "result": False,
        "message": message,
        "error_code": error_code
    } 