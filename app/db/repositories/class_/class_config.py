from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseRepository
from app.db.models.class_ import ClassTemplate
from app.schemas.class_.class_ import ClassConfig, ClassConfigCreate, ClassConfigUpdate
from app.db.repositories.class_.class_ import class_repository

class ClassConfigRepository(BaseRepository[ClassTemplate, ClassConfigCreate, ClassConfigUpdate]):
    async def update_class_config(self, db: AsyncSession, obj_in: ClassConfig) -> ClassTemplate:
        class_config = await self.get_class_config(db=db)
    
        if not class_config:
            class_config = ClassTemplate()
            db.add(class_config)
        
        class_config.specializations = obj_in.specializations
        class_config.grade_levels = obj_in.grade_levels
        class_config.letters = obj_in.letters
        
        await db.commit()
        await db.refresh(class_config)
        
        return class_config
    
    async def get_class_config(self, db: AsyncSession) -> Optional[ClassTemplate]:
        class_config = await db.scalar(
            select(ClassTemplate).order_by(ClassTemplate.id).limit(1)
        )
        return class_config

    async def get_free_letters(self, db: AsyncSession, grade_level: int) -> Optional[List[str]]:
        class_config = await self.get_class_config(db=db)
        if not class_config:
            return []

        letters = class_config.letters
        existing_letters = await class_repository.get_existing_letters(db=db, grade_level=grade_level)
        return [letter for letter in letters if letter not in existing_letters]
    
class_config_repository = ClassConfigRepository(ClassTemplate) 