from fastapi import APIRouter
import logging
from app.core.logger import setup_logging
from app.schemas.base import BaseResponse, ErrorResponse, success_response, error_response
from app.schemas.academic_cycles.academic_year import AcademicYearList, AcademicYearCreate
from typing import List, Union
from app.db.repositories.academic_cycles.academic_years import academic_years_repository
from app.db.session import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.user.user import User, UserRole
from fastapi import Depends
from app.services.academic_cycles import create_academic_year

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["academic_cycles"])

@router.post("/", response_model=Union[BaseResponse[AcademicYearList], ErrorResponse])
async def create_academic_year_endpoint(academic_year: AcademicYearCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Создание нового академического года с проверкой на пересечения дат и названий.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
            
        created_academic_year = await create_academic_year(db=db, academic_year=academic_year)
        return success_response(
            data=created_academic_year,
            message="Academic year created successfully"
        )
    except ValueError as e:
        logger.error(f"VALIDATION_ERROR: {e}")
        return error_response(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )
    except Exception as e:
        logger.error(f"CREATE_ACADEMIC_YEAR_ERROR: {e}")
        return error_response(
            message="Failed to create academic year",
            error_code="CREATE_ACADEMIC_YEAR_ERROR"
        )

@router.get("/", response_model=Union[BaseResponse[List[AcademicYearList]], ErrorResponse])
async def get_academic_years(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    """
    Получение списка всех академических лет с поддержкой пагинации.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        academic_years = await academic_years_repository.get_all(db=db,skip=skip, limit=limit)
        academic_years = [AcademicYearList.model_validate(academic_year) for academic_year in academic_years]
        
        return success_response(
            data=academic_years,
            message="Academic years retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_ACADEMIC_YEARS_ERROR: {e}")
        return error_response(
            message="Failed to get academic years",
            error_code="GET_ACADEMIC_YEARS_ERROR"
        )
        
@router.get("/current", response_model=Union[BaseResponse[AcademicYearList], ErrorResponse])
async def get_current_academic_year(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    """
    Получение текущего активного академического года.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        academic_year = await academic_years_repository.get_current_academic_year(db=db)
        if not academic_year:
            return error_response(
                message="No current academic year found",
                error_code="NO_CURRENT_ACADEMIC_YEAR_FOUND"
            )
            
        academic_year = AcademicYearList.model_validate(academic_year)
        return success_response(
            data=academic_year,
            message="Current academic year retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_CURRENT_ACADEMIC_YEAR_ERROR: {e}")
        return error_response(
            message="Failed to get current academic year",
            error_code="GET_CURRENT_ACADEMIC_YEAR_ERROR"
        )
        
@router.get("/{academic_year_id}", response_model=Union[BaseResponse[AcademicYearList], ErrorResponse])
async def get_academic_year_with_periods(academic_year_id: int, db = Depends(get_db), _: User = Depends(get_current_user)):
    """
    Получение конкретного академического года с периодами по ID.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        academic_year = await academic_years_repository.get_with_periods(db=db, academic_year_id=academic_year_id)
        if not academic_year:
            return error_response(
                message="Academic year not found",
                error_code="ACADEMIC_YEAR_NOT_FOUND"
            )
        academic_year = AcademicYearList.model_validate(academic_year)
        return success_response(
            data=academic_year,
            message="Academic year retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_ACADEMIC_YEAR_ERROR: {e}")
        return error_response(
            message="Failed to get academic year",
            error_code="GET_ACADEMIC_YEAR_ERROR"
        )
        
