
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

from app.db.repositories.file import file_repository
from app.schemas.file import File, FileCreate
from app.services.minio import MinioService, get_minio_service
from app.core.dependencies import get_current_user
from app.schemas.auth import User


router = APIRouter(tags=["files"])

@router.post("/", response_model=File)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
    _: User = Depends(get_current_user)
):
    """Загрузка файла в хранилище."""
    try:
        # Загружаем файл в MinIO
        object_name = await minio_service.upload_file(
            file=file
        )
        
        # Получаем размер файла
        file_data = await file.read()
        file_size = len(file_data)
        await file.seek(0)
        
        # Создаем запись в БД о файле
        file_create = FileCreate(
            filename=object_name.split("/")[-1],
            original_filename=file.filename or "file",
            bucket_name=settings.MINIO_PUBLIC_BUCKET,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream",
            size=file_size,
        )
        
        db_file = await file_repository.create(db=db, obj_in=file_create)
        
        file_url = await minio_service.get_direct_file_url(
            bucket_name=settings.MINIO_PUBLIC_BUCKET,
            object_name=object_name
        )
        
        result = File.model_validate(db_file)
        result.url = file_url
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")

@router.get("/{file_id}", response_model=File)
async def get_file_by_id(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
    _: User = Depends(get_current_user),
):
    """Получение информации о файле с URL для доступа."""
    db_file = await file_repository.get(db=db, id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    file_url = await minio_service.get_direct_file_url(
        bucket_name=settings.MINIO_PUBLIC_BUCKET,
        object_name=db_file.object_name
    )
    
    result = File.model_validate(db_file)
    result.url = file_url
    
    return result