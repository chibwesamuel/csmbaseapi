import uuid

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
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


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class OrganizationInvitation(Base):
    __tablename__ = "organization_invitations"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "email",
            name="uq_org_invitation_email",
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

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "roles.id"
        ),
        nullable=False,
    )

    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id"
        ),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[InvitationStatus] = mapped_column(
        SqlEnum(
            InvitationStatus,
            name="invitationstatus",
            values_callable=lambda enum: [
                item.value for item in enum
            ],
        ),
        default=InvitationStatus.PENDING,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


    # -----------------------------
    # Relationships
    # -----------------------------

    organization = relationship(
        "Organization",
        back_populates="invitations",
    )

    role = relationship(
        "Role",
        back_populates="organization_invitations",
    )

    inviter = relationship(
        "User",
        foreign_keys=[invited_by],
        back_populates="sent_invitations",
    )


    def __repr__(self):
        return (
            f"<OrganizationInvitation("
            f"id={self.id}, "
            f"email='{self.email}', "
            f"status='{self.status}')>"
        )