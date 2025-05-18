"""add_default_admin_user

Revision ID: 7af9b59e77b6
Revises: d6d803865fb3
Create Date: 2025-05-19 00:05:47.311176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash
from app.db.models.user import UserRole

# revision identifiers, used by Alembic.
revision: str = '7af9b59e77b6'
down_revision: Union[str, None] = 'd6d803865fb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем соединение с БД
    bind = op.get_bind()
    Base = declarative_base()
    
    # Определяем модель User для текущей миграции
    class User(Base):
        __tablename__ = "users"
        
        id = sa.Column(sa.Integer, primary_key=True, index=True)
        email = sa.Column(sa.String, unique=True, index=True, nullable=False)
        username = sa.Column(sa.String, unique=True, index=True, nullable=False)
        hashed_password = sa.Column(sa.String, nullable=False)
        role = sa.Column(sa.Enum(UserRole), nullable=False)
        full_name = sa.Column(sa.String)
        is_active = sa.Column(sa.Boolean, default=True)
    
    # Создаем сессию
    Session = sessionmaker(bind=bind)
    session = Session()
    
    # Проверяем, существует ли уже администратор
    admin_exists = session.query(User).filter(User.username == "admin").first()
    
    # Если администратор не существует, создаем его
    if not admin_exists:
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin"),
            role=UserRole.ADMIN,
            full_name="Администратор",
            is_active=True
        )
        session.add(admin)
        session.commit()
    
    session.close()


def downgrade() -> None:
    pass