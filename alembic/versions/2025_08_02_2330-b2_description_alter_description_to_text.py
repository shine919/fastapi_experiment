"""Alter description to Text

Revision ID: b2_description
Revises: a2_featured
Create Date: 2025-08-02 23:30:17.175727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2_description'
down_revision: Union[str, Sequence[str], None] = '7de4e7e8fb64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
    'products',
    'description',
    existing_type=sa.String(length=120),
    type_=sa.Text(),
    nullable=False,
)


def downgrade() -> None:
    op.alter_column(
    'products',
    'description',
    existing_type=sa.Text(),
    type_=sa.String(length=120),
    nullable=True,
)
