"""recorded_expenses

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-30 10:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: str | Sequence[str] | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "expense_names",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("normalized_label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_label"),
    )
    op.create_table(
        "expense_categories",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("normalized_label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_label"),
    )
    op.create_table(
        "expense_places",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("normalized_label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_label"),
    )
    op.create_table(
        "recorded_expenses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("occurred_on", sa.String(), nullable=False),
        sa.Column("name_id", sa.String(), nullable=False),
        sa.Column("category_id", sa.String(), nullable=True),
        sa.Column("place_id", sa.String(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["expense_categories.id"]),
        sa.ForeignKeyConstraint(["name_id"], ["expense_names.id"]),
        sa.ForeignKeyConstraint(["place_id"], ["expense_places.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("recorded_expenses", schema=None) as batch_op:
        batch_op.create_index(
            "ix_recorded_expenses_occurred_on",
            ["occurred_on"],
            unique=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("recorded_expenses", schema=None) as batch_op:
        batch_op.drop_index("ix_recorded_expenses_occurred_on")

    op.drop_table("recorded_expenses")
    op.drop_table("expense_places")
    op.drop_table("expense_categories")
    op.drop_table("expense_names")
