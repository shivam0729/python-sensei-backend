"""add processing status

Revision ID: 70c7c2f7c5dd
Revises: 19dbd5c5bee7
Create Date: 2026-05-26 23:54:00.758166

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '70c7c2f7c5dd'
down_revision: Union[str, Sequence[str], None] = '19dbd5c5bee7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add processing_status column
    op.add_column(
        'resume',
        sa.Column(
            'processing_status',
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="pending"
        )
    )

    # Add processing_error column
    op.add_column(
        'resume',
        sa.Column(
            'processing_error',
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('resume', 'processing_error')

    op.drop_column('resume', 'processing_status')