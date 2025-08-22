"""b2 and a2 merge

Revision ID: cedafc6780b8
Revises: a2_featured, b2_description
Create Date: 2025-08-02 23:42:33.728548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cedafc6780b8'
down_revision: Union[str, Sequence[str], None] = ('a2_featured', 'b2_description')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
