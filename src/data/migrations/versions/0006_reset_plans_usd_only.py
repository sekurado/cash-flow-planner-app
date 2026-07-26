"""reset_plans_usd_only

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-27 10:00:00.000000

Deletes all existing plans (cascade removes entries and simulation runs).
Exchange rates are global and retained. Non-USD-target rate rows are removed.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: str | Sequence[str] | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove all plans and non-USD exchange-rate targets."""
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM plans"))
    connection.execute(
        sa.text("DELETE FROM exchange_rates WHERE to_currency != 'USD'")
    )


def downgrade() -> None:
    """No-op: deleted plan data cannot be restored."""
