"""update relations and add user_invites

Revision ID: 7f5278b1e51a
Revises: 68d82b1f0f44
Create Date: 2025-05-21 21:38:55.199200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7f5278b1e51a'
down_revision: Union[str, None] = '68d82b1f0f44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    userrole_enum = postgresql.ENUM(
        'admin', 'teacher', 'student', 
        name='userrole',
        create_type=False  
    )
    op.create_table('user_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('invite_code', sa.String(), nullable=False),
        sa.Column('role', userrole_enum, nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_invites_id'), 'user_invites', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_invites_id'), table_name='user_invites')
    op.drop_table('user_invites')
    op.execute('DROP TYPE IF EXISTS userroles')