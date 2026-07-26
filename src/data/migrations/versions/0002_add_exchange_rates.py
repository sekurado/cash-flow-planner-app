"""add_exchange_rates

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-23 10:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("plan_id", sa.String(), nullable=False),
        sa.Column("from_currency", sa.String(), nullable=False),
        sa.Column("to_currency", sa.String(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("effective_date", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("exchange_rates", schema=None) as batch_op:
        batch_op.create_index("ix_exchange_rates_plan_id", ["plan_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("exchange_rates", schema=None) as batch_op:
        batch_op.drop_index("ix_exchange_rates_plan_id")

    op.drop_table("exchange_rates")
