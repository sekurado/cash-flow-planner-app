"""global_exchange_rates

Revision ID: 0005
Revises: 0003
Create Date: 2026-06-26 10:00:00.000000

Migrates exchange_rates from per-plan rows (UUID PK, effective_date) to a single
global lookup keyed by (from_currency, to_currency). Downgrade recreates the
plan-scoped table; per-plan rate rows are not restored (data loss on downgrade).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Replace plan-scoped exchange_rates with a global currency-pair table."""
    op.create_table(
        "exchange_rates_new",
        sa.Column("from_currency", sa.String(), nullable=False),
        sa.Column("to_currency", sa.String(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("from_currency", "to_currency"),
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT OR REPLACE INTO exchange_rates_new (from_currency, to_currency, rate, updated_at)
            SELECT e.from_currency, e.to_currency, e.rate, e.effective_date
            FROM exchange_rates e
            INNER JOIN (
                SELECT from_currency, to_currency, MAX(effective_date) AS max_date
                FROM exchange_rates
                GROUP BY from_currency, to_currency
            ) latest
                ON e.from_currency = latest.from_currency
                AND e.to_currency = latest.to_currency
                AND e.effective_date = latest.max_date
            """
        )
    )

    with op.batch_alter_table("exchange_rates", schema=None) as batch_op:
        batch_op.drop_index("ix_exchange_rates_plan_id")

    op.drop_table("exchange_rates")
    op.rename_table("exchange_rates_new", "exchange_rates")


def downgrade() -> None:
    """Recreate plan-scoped exchange_rates. Global rate rows are discarded."""
    op.create_table(
        "exchange_rates_new",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("plan_id", sa.String(), nullable=False),
        sa.Column("from_currency", sa.String(), nullable=False),
        sa.Column("to_currency", sa.String(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("effective_date", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("exchange_rates_new", schema=None) as batch_op:
        batch_op.create_index("ix_exchange_rates_plan_id", ["plan_id"], unique=False)

    op.drop_table("exchange_rates")
    op.rename_table("exchange_rates_new", "exchange_rates")
