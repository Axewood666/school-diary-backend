from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Optional

from app.schemas.base import error_response, BaseResponse, ErrorResponse, success_response
from app.schemas.user import UserRole, User
from app.schemas.academic_cycles import (
    AcademicYearCreate, AcademicYearUpdate, AcademicYearList,
    AcademicPeriodCreate, AcademicPeriodUpdate, AcademicPeriodList,
    AcademicWeekCreate, AcademicWeekUpdate, AcademicWeekList
)

from app.core.dependencies import get_db, get_current_user
from app.core.logger import setup_logging
from app.db.repositories.academic_cycles import academic_cycles_repository
from app.db.models.academic_cycles import AcademicPeriod, AcademicWeek
from app.db.base import BaseRepository

import logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["academic-cycles"])

# Academic Year endpoints
@router.get("/years", response_model=Union[BaseResponse[List[AcademicYearList]], ErrorResponse])
async def get_academic_years(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список учебных годов"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        years = await academic_cycles_repository.get_multi(db=db, skip=skip, limit=limit)
        
        year_list = [
            AcademicYearList(
                id=year.id,
                name=year.name,
                start_date=year.start_date,
                end_date=year.end_date,
                is_current=year.is_current,
                created_at=year.created_at
            ) for year in years
        ]

        return success_response(
            data=year_list,
            message="Учебные годы успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_ACADEMIC_YEARS_ERROR: {e}")
        return error_response(
            message="Не удалось получить учебные годы",
            error_code="GET_ACADEMIC_YEARS_ERROR"
        )

@router.post("/years", response_model=Union[BaseResponse[AcademicYearList], ErrorResponse])
async def create_academic_year(
    year_create: AcademicYearCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать учебный год"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        year = await academic_cycles_repository.create(db=db, obj_in=year_create)

        return success_response(
            data=AcademicYearList(
                id=year.id,
                name=year.name,
                start_date=year.start_date,
                end_date=year.end_date,
                is_current=year.is_current,
                created_at=year.created_at
            ),
            message="Учебный год успешно создан"
        )
    except Exception as e:
        logger.error(f"CREATE_ACADEMIC_YEAR_ERROR: {e}")
        return error_response(
            message="Не удалось создать учебный год",
            error_code="CREATE_ACADEMIC_YEAR_ERROR"
        )

@router.get("/current-year", response_model=Union[BaseResponse[AcademicYearList], ErrorResponse])
async def get_current_academic_year(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить текущий учебный год"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        year = await academic_cycles_repository.get_current_academic_year(db=db)
        if not year:
            return error_response(
                message="Текущий учебный год не найден",
                error_code="CURRENT_YEAR_NOT_FOUND"
            )

        return success_response(
            data=AcademicYearList(
                id=year.id,
                name=year.name,
                start_date=year.start_date,
                end_date=year.end_date,
                is_current=year.is_current,
                created_at=year.created_at
            ),
            message="Текущий учебный год успешно получен"
        )
    except Exception as e:
        logger.error(f"GET_CURRENT_ACADEMIC_YEAR_ERROR: {e}")
        return error_response(
            message="Не удалось получить текущий учебный год",
            error_code="GET_CURRENT_ACADEMIC_YEAR_ERROR"
        )

# Academic Period endpoints
@router.get("/periods", response_model=Union[BaseResponse[List[AcademicPeriodList]], ErrorResponse])
async def get_academic_periods(
    year_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список учебных периодов"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        if year_id:
            periods = await academic_cycles_repository.get_academic_periods_by_year(db=db, year_id=year_id)
        else:
            # Получаем периоды текущего года
            current_year = await academic_cycles_repository.get_current_academic_year(db=db)
            if not current_year:
                return error_response(
                    message="Текущий учебный год не найден",
                    error_code="CURRENT_YEAR_NOT_FOUND"
                )
            periods = await academic_cycles_repository.get_academic_periods_by_year(db=db, year_id=current_year.id)

        period_list = []
        for period in periods:
            # Получаем год для каждого периода
            year = await academic_cycles_repository.get_academic_year_by_id(db=db, id=period.year_id)
            period_list.append(AcademicPeriodList(
                id=period.id,
                year_id=period.year_id,
                year_name=year.name if year else "Неизвестно",
                name=period.name,
                order_num=period.order_num,
                start_date=period.start_date,
                end_date=period.end_date,
                is_current=period.is_current,
                created_at=period.created_at
            ))

        return success_response(
            data=period_list,
            message="Учебные периоды успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_ACADEMIC_PERIODS_ERROR: {e}")
        return error_response(
            message="Не удалось получить учебные периоды",
            error_code="GET_ACADEMIC_PERIODS_ERROR"
        )

@router.get("/current-period", response_model=Union[BaseResponse[AcademicPeriodList], ErrorResponse])
async def get_current_academic_period(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить текущий учебный период"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        period = await academic_cycles_repository.get_current_academic_period(db=db)
        if not period:
            return error_response(
                message="Текущий учебный период не найден",
                error_code="CURRENT_PERIOD_NOT_FOUND"
            )

        year = await academic_cycles_repository.get_academic_year_by_id(db=db, id=period.year_id)

        return success_response(
            data=AcademicPeriodList(
                id=period.id,
                year_id=period.year_id,
                year_name=year.name if year else "Неизвестно",
                name=period.name,
                order_num=period.order_num,
                start_date=period.start_date,
                end_date=period.end_date,
                is_current=period.is_current,
                created_at=period.created_at
            ),
            message="Текущий учебный период успешно получен"
        )
    except Exception as e:
        logger.error(f"GET_CURRENT_ACADEMIC_PERIOD_ERROR: {e}")
        return error_response(
            message="Не удалось получить текущий учебный период",
            error_code="GET_CURRENT_ACADEMIC_PERIOD_ERROR"
        )

# Academic Week endpoints
@router.get("/weeks", response_model=Union[BaseResponse[List[AcademicWeekList]], ErrorResponse])
async def get_academic_weeks(
    period_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список учебных недель"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        if period_id:
            weeks = await academic_cycles_repository.get_academic_weeks_by_period(db=db, period_id=period_id)
        else:
            # Получаем недели текущего периода
            current_period = await academic_cycles_repository.get_current_academic_period(db=db)
            if not current_period:
                return error_response(
                    message="Текущий учебный период не найден",
                    error_code="CURRENT_PERIOD_NOT_FOUND"
                )
            weeks = await academic_cycles_repository.get_academic_weeks_by_period(db=db, period_id=current_period.id)

        week_list = []
        for week in weeks:
            # Получаем период для каждой недели
            period_repo = BaseRepository(AcademicPeriod)
            period = await period_repo.get(db=db, id=week.period_id)
            week_list.append(AcademicWeekList(
                id=week.id,
                period_id=week.period_id,
                period_name=period.name if period else "Неизвестно",
                week_num=week.week_num,
                name=week.name,
                start_date=week.start_date,
                end_date=week.end_date,
                is_holiday=week.is_holiday,
                created_at=week.created_at
            ))

        return success_response(
            data=week_list,
            message="Учебные недели успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_ACADEMIC_WEEKS_ERROR: {e}")
        return error_response(
            message="Не удалось получить учебные недели",
            error_code="GET_ACADEMIC_WEEKS_ERROR"
        )

@router.get("/current-week", response_model=Union[BaseResponse[AcademicWeekList], ErrorResponse])
async def get_current_academic_week(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить текущую учебную неделю"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        week = await academic_cycles_repository.get_current_academic_week(db=db)
        if not week:
            return error_response(
                message="Текущая учебная неделя не найдена",
                error_code="CURRENT_WEEK_NOT_FOUND"
            )

        period_repo = BaseRepository(AcademicPeriod)
        period = await period_repo.get(db=db, id=week.period_id)

        return success_response(
            data=AcademicWeekList(
                id=week.id,
                period_id=week.period_id,
                period_name=period.name if period else "Неизвестно",
                week_num=week.week_num,
                name=week.name,
                start_date=week.start_date,
                end_date=week.end_date,
                is_holiday=week.is_holiday,
                created_at=week.created_at
            ),
            message="Текущая учебная неделя успешно получена"
        )
    except Exception as e:
        logger.error(f"GET_CURRENT_ACADEMIC_WEEK_ERROR: {e}")
        return error_response(
            message="Не удалось получить текущую учебную неделю",
            error_code="GET_CURRENT_ACADEMIC_WEEK_ERROR"
        ) 