"""Add PROCESSING and FAILED status, result_path and completed_at fields

Revision ID: 003_add_processing_status
Revises: 002_add_file_path
Create Date: 2025-10-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_processing_status'
down_revision: Union[str, None] = '002_add_file_path'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add result_path column to tasks table
    op.add_column(
        'tasks',
        sa.Column('result_path', sa.String(length=500), nullable=True)
    )
    
    # Add completed_at column to tasks table
    op.add_column(
        'tasks',
        sa.Column('completed_at', sa.DateTime(), nullable=True)
    )
    
    # Update the TaskStatus enum to include PROCESSING and FAILED
    # Note: For PostgreSQL, we need to add the new enum values
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'processing' BEFORE 'in_progress'")
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'failed' BEFORE 'cancelled'")


def downgrade() -> None:
    # Remove new columns
    op.drop_column('tasks', 'completed_at')
    op.drop_column('tasks', 'result_path')
    
    # Note: PostgreSQL doesn't support removing enum values easily
    # You would need to recreate the enum type to remove values
    # This is left as a manual operation if needed
