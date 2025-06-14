"""remove auth fields

Revision ID: 9cea6ef7e6f7
Revises: 1
Create Date: 2025-06-13 05:02:43.837178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cea6ef7e6f7'
down_revision: Union[str, None] = '1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profile', 'password')
    op.drop_column('profile', 'is_active')
    op.drop_column('profile', 'login')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profile', sa.Column('login', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('profile', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('profile', sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
