from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any, List
from app.schemas.auth import Token, UserInviteInfo
from app.schemas.role import User, Student, UserResponse, Teacher

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

class LoginSuccessResponse(Token):
    result: bool = True

class PaginationInfo(BaseModel):
    skip: int
    limit: int
    total: int

class InviteListData(BaseModel):
    invites: List[UserInviteInfo]
    pagination: PaginationInfo

class UsersListData(BaseModel):
    users: List[User]
    pagination: PaginationInfo

class UserWithStudentInfo(BaseModel):
    user_info: UserResponse
    student_info: Student
    

class StudentsListData(BaseModel):
    students: List[UserWithStudentInfo]  
    pagination: PaginationInfo

class UserWithTeacherInfo(BaseModel):
    user_info: UserResponse
    teacher_info: Teacher

class TeachersListData(BaseModel):
    teachers: List[UserWithTeacherInfo] 
    pagination: PaginationInfo

class AdminsListData(BaseModel):
    admins: List[User]
    pagination: PaginationInfo

class UserDeactivateData(BaseModel):
    is_deactivated: bool

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