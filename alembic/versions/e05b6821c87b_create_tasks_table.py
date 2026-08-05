"""create tasks table

Revision ID: e05b6821c87b
Revises: d123e09cbaaa
Create Date: 2026-08-05 14:13:24.376892

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e05b6821c87b"
down_revision: Union[str, Sequence[str], None] = "d123e09cbaaa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "tasks",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "assigned_to",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "title",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "due_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["assigned_to"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_tasks_project_id",
        "tasks",
        ["project_id"],
    )

    op.create_index(
        "ix_tasks_assigned_to",
        "tasks",
        ["assigned_to"],
    )

    op.create_index(
        "ix_tasks_status",
        "tasks",
        ["status"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_tasks_status",
        table_name="tasks",
    )

    op.drop_index(
        "ix_tasks_assigned_to",
        table_name="tasks",
    )

    op.drop_index(
        "ix_tasks_project_id",
        table_name="tasks",
    )

    op.drop_table("tasks")