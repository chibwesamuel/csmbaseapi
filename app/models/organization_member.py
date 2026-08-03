import uuid

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


class OrganizationMember(Base):
    """
    Represents a user's membership within an organization.

    A user may belong to many organizations,
    but only once per organization.

    Organization permissions are determined
    by the assigned organization role.
    """

    __tablename__ = "organization_members"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_member",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "roles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships

    organization = relationship(
        "Organization",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="organizations",
    )

    role = relationship(
        "Role",
        back_populates="organization_members",
    )

    def __repr__(self) -> str:
        return (
            "<OrganizationMember("
            f"id={self.id}, "
            f"organization_id={self.organization_id}, "
            f"user_id={self.user_id}, "
            f"role_id={self.role_id}"
            ")>"
        )