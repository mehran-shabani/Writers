"""Add file_path column to tasks table

Revision ID: 002_add_file_path
Revises: 001_initial
Create Date: 2025-10-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_file_path'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add file_path column to tasks table
    op.add_column(
        'tasks',
        sa.Column('file_path', sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    # Remove file_path column from tasks table
    op.drop_column('tasks', 'file_path')
