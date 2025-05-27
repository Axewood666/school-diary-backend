from fastapi import APIRouter
import logging
from app.core.logger import setup_logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["academic_cycles"])

@router.get("/", response_model=Union[BaseResponse[List[AcademicCycleList]], ErrorResponse])
async def get_academic_cycles():
    return {"message": "Hello, World!"}