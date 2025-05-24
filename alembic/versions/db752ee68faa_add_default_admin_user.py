"""add default admin user

Revision ID: db752ee68faa
Revises: 7f5278b1e51a
Create Date: 2025-05-21 22:45:40.361195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.db.models.user import UserRole
from app.core.security import pwd_context

revision: str = 'db752ee68faa'
down_revision: Union[str, None] = '7f5278b1e51a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_password_hash(password: str) -> str:
    """
    Копия функции из app.core.security для обеспечения одинакового хеширования
    """
    return pwd_context.hash(password)


def upgrade() -> None:
    bind = op.get_bind()
    Base = declarative_base()
    
    class User(Base):
        __tablename__ = "users"
        
        id = sa.Column(sa.Integer, primary_key=True, index=True)
        email = sa.Column(sa.String, unique=True, index=True, nullable=False)
        username = sa.Column(sa.String, unique=True, index=True, nullable=False)
        hashed_password = sa.Column(sa.String, nullable=False)
        role = sa.Column(sa.Enum(UserRole), nullable=False)
        full_name = sa.Column(sa.String)
        is_active = sa.Column(sa.Boolean, default=True)
    
    Session = sessionmaker(bind=bind)
    session = Session()
    
    admin_exists = session.query(User).filter(User.username == "admin").first()
    if not admin_exists:
        hashed_password = get_password_hash("admin")
        
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            full_name="Администратор",
            is_active=True
        )
        session.add(admin)
        session.commit()
    
    session.close()


def downgrade() -> None:
    pass