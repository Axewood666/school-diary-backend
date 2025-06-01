from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, update
from app.db.models.academic_cycles import AcademicYear
from app.schemas.academic_cycles.academic_year import AcademicYearCreate, AcademicYearList
from app.db.repositories.academic_cycles.academic_years import academic_years_repository

async def create_academic_year(db: AsyncSession, academic_year: AcademicYearCreate) -> AcademicYearList:
    """
    Создает год(с проверкой на пересечения по датам и названию).
    """
    try:
        query = select(AcademicYear).where(
            or_(
                AcademicYear.name == academic_year.name,
                or_(
                    AcademicYear.start_date.between(academic_year.start_date, academic_year.end_date),
                    AcademicYear.end_date.between(academic_year.start_date, academic_year.end_date),
                    and_(
                        academic_year.start_date <= AcademicYear.start_date,
                        academic_year.end_date >= AcademicYear.end_date
                    )
                )
            )
        )
        
        result = await db.execute(query)
        existing_year = result.scalar_one_or_none()
        
        if existing_year:
            if existing_year.name == academic_year.name:
                raise ValueError(f"Academic year with name '{academic_year.name}' already exists")
            else:
                raise ValueError(f"Academic year dates overlap with existing year '{existing_year.name}'")
        
        if academic_year.is_current:
            await db.execute(
                update(AcademicYear).values(is_current=False).where(AcademicYear.is_current == True)
            )
        
        created_year = await academic_years_repository.create(db=db, obj_in=academic_year)
        
        return AcademicYearList.model_validate(created_year)
        
    except Exception as e:
        await db.rollback()
        raise e