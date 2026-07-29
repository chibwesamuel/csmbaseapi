from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.organization_invitation import (
    OrganizationInvitation,
    InvitationStatus,
)


def create_invitation(
    db: Session,
    invitation: OrganizationInvitation,
) -> OrganizationInvitation:
    """
    Create a new organization invitation.
    """

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation


def get_invitation_by_id(
    db: Session,
    invitation_id: UUID,
) -> OrganizationInvitation | None:
    """
    Retrieve an invitation by ID.
    """

    return (
        db.query(OrganizationInvitation)
        .options(
            joinedload(
                OrganizationInvitation.organization
            ),
            joinedload(
                OrganizationInvitation.role
            ),
            joinedload(
                OrganizationInvitation.inviter
            ),
        )
        .filter(
            OrganizationInvitation.id == invitation_id
        )
        .first()
    )


def get_invitation_by_token(
    db: Session,
    token: str,
) -> OrganizationInvitation | None:
    """
    Retrieve an invitation using its token.
    """

    return (
        db.query(OrganizationInvitation)
        .options(
            joinedload(
                OrganizationInvitation.organization
            ),
            joinedload(
                OrganizationInvitation.role
            ),
        )
        .filter(
            OrganizationInvitation.token == token
        )
        .first()
    )


def get_pending_invitation_by_email(
    db: Session,
    organization_id: UUID,
    email: str,
) -> OrganizationInvitation | None:
    """
    Retrieve an active pending invitation
    for an email in an organization.
    """

    return (
        db.query(OrganizationInvitation)
        .filter(
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.email == email,
            OrganizationInvitation.status
            == InvitationStatus.PENDING,
        )
        .first()
    )


def get_organization_invitations(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
) -> list[OrganizationInvitation]:
    """
    Retrieve invitations belonging to an organization.
    """

    return (
        db.query(OrganizationInvitation)
        .options(
            joinedload(
                OrganizationInvitation.role
            ),
            joinedload(
                OrganizationInvitation.inviter
            ),
        )
        .filter(
            OrganizationInvitation.organization_id
            == organization_id
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_organization_invitations(
    db: Session,
    organization_id: UUID,
) -> int:
    """
    Count invitations belonging to an organization.
    """

    return (
        db.query(OrganizationInvitation)
        .filter(
            OrganizationInvitation.organization_id
            == organization_id
        )
        .count()
    )


def update_invitation_status(
    db: Session,
    invitation: OrganizationInvitation,
    status: InvitationStatus,
) -> OrganizationInvitation:
    """
    Update invitation status.
    """

    invitation.status = status

    db.commit()
    db.refresh(invitation)

    return invitation


def delete_invitation(
    db: Session,
    invitation: OrganizationInvitation,
) -> bool:
    """
    Delete an invitation.
    """

    db.delete(invitation)
    db.commit()

    return True