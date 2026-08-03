"""replace organization member role with role_id

Revision ID: 0c8b0a848fad
Revises: 9610eccce09b
Create Date: 2026-08-03 17:18:08.854516

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0c8b0a848fad"
down_revision: Union[str, Sequence[str], None] = "9610eccce09b"
branch_labels = None
depends_on = None


def upgrade() -> None:

    connection = op.get_bind()

    # Add role_id column
    op.add_column(
        "organization_members",
        sa.Column(
            "role_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # Fetch only organization roles
    roles = connection.execute(
        sa.text(
            """
            SELECT id, name
            FROM roles
            WHERE LOWER(name) IN (
                'owner',
                'admin',
                'member'
            )
            """
        )
    ).fetchall()

    role_map = {
        row.name.lower(): row.id
        for row in roles
    }

    # Assign existing string roles to role IDs
    members = connection.execute(
        sa.text(
            """
            SELECT id, role
            FROM organization_members
            """
        )
    ).fetchall()

    for member in members:

        role_id = role_map.get(
            member.role.lower()
        )

        if role_id is None:
            raise Exception(
                f"Missing role mapping for {member.role}"
            )

        connection.execute(
            sa.text(
                """
                UPDATE organization_members
                SET role_id = :role_id
                WHERE id = :id
                """
            ),
            {
                "role_id": role_id,
                "id": member.id,
            },
        )

    # Make role_id required
    op.alter_column(
        "organization_members",
        "role_id",
        nullable=False,
    )

    # Add foreign key
    op.create_foreign_key(
        "fk_organization_members_role_id",
        "organization_members",
        "roles",
        ["role_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # Remove old role column
    op.drop_column(
        "organization_members",
        "role",
    )


def downgrade() -> None:

    connection = op.get_bind()

    # Restore old role column
    op.add_column(
        "organization_members",
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=True,
        ),
    )

    roles = connection.execute(
        sa.text(
            """
            SELECT id, name
            FROM roles
            """
        )
    ).fetchall()

    role_map = {
        str(row.id): row.name
        for row in roles
    }

    members = connection.execute(
        sa.text(
            """
            SELECT id, role_id
            FROM organization_members
            """
        )
    ).fetchall()

    for member in members:

        connection.execute(
            sa.text(
                """
                UPDATE organization_members
                SET role = :role
                WHERE id = :id
                """
            ),
            {
                "role": role_map.get(
                    str(member.role_id)
                ),
                "id": member.id,
            },
        )

    op.drop_constraint(
        "fk_organization_members_role_id",
        "organization_members",
        type_="foreignkey",
    )

    op.drop_column(
        "organization_members",
        "role_id",
    )