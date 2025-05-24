from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

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

class PaginationInfo(BaseModel):
    skip: int
    limit: int
    total: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationInfo

def success_response(data, message: str = "Success") -> dict:
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