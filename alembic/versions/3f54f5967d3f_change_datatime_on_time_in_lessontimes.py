"""change datatime on time in lessontimes

Revision ID: 3f54f5967d3f
Revises: 721eb1495115
Create Date: 2025-05-25 12:35:31.445091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f54f5967d3f'
down_revision: Union[str, None] = '721eb1495115'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('lesson_times', 'start_time', type_=sa.Time(), existing_type=sa.DateTime())
    op.alter_column('lesson_times', 'end_time', type_=sa.Time(), existing_type=sa.DateTime())
    pass


def downgrade() -> None:
    op.alter_column('lesson_times', 'start_time', type_=sa.DateTime(), existing_type=sa.Time())
    op.alter_column('lesson_times', 'end_time', type_=sa.DateTime(), existing_type=sa.Time())
    pass