"""expand organization model

Revision ID: 47ad7b6204d2
Revises: 735ad6fcbafa
Create Date: 2026-07-22 10:04:32.322488
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "47ad7b6204d2"
down_revision: Union[str, Sequence[str], None] = "735ad6fcbafa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "organizations",
        sa.Column("email", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("phone", sa.String(length=30), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("website", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("logo_url", sa.String(length=500), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("address", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("city", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("country", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("timezone", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "organizations",
        sa.Column("currency", sa.String(length=10), nullable=True),
    )

    # Add with a temporary default so existing rows are populated.
    op.add_column(
        "organizations",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # Remove the default so future inserts rely on the application.
    op.alter_column(
        "organizations",
        "is_active",
        server_default=None,
    )

    op.create_unique_constraint(
        "uq_organizations_email",
        "organizations",
        ["email"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_organizations_email",
        "organizations",
        type_="unique",
    )

    op.drop_column("organizations", "is_active")
    op.drop_column("organizations", "currency")
    op.drop_column("organizations", "timezone")
    op.drop_column("organizations", "country")
    op.drop_column("organizations", "city")
    op.drop_column("organizations", "address")
    op.drop_column("organizations", "logo_url")
    op.drop_column("organizations", "website")
    op.drop_column("organizations", "phone")
    op.drop_column("organizations", "email")