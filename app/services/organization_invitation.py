from datetime import datetime, timedelta, timezone
import secrets

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization_invitation import (
    OrganizationInvitation,
    InvitationStatus,
)

from app.models.organization_member import (
    OrganizationMember,
)

from app.repositories.organization import (
    get_organization_by_id,
)

from app.repositories.organization_member import (
    get_member,
)

from app.repositories.organization_invitation import (
    create_invitation,
    get_invitation_by_token,
    get_pending_invitation_by_email,
    get_invitation_by_id,
    update_invitation_status,
    delete_invitation,
)

from app.repositories.role import (
    get_role_by_id,
)


INVITATION_EXPIRY_DAYS = 7


def generate_invitation_token() -> str:
    """
    Generate a secure invitation token.
    """

    return secrets.token_urlsafe(32)



def create_organization_invitation(
    db: Session,
    organization_id: UUID,
    role_id: UUID,
    email: str,
    invited_by: UUID,
) -> OrganizationInvitation:
    """
    Create an organization invitation.
    """

    organization = get_organization_by_id(
        db,
        organization_id,
    )

    if not organization:
        raise ValueError(
            "Organization not found"
        )


    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        raise ValueError(
            "Role not found"
        )


    existing_invitation = (
        get_pending_invitation_by_email(
            db,
            organization_id,
            email,
        )
    )

    if existing_invitation:
        raise ValueError(
            "A pending invitation already exists for this email"
        )


    invitation = OrganizationInvitation(
        organization_id=organization_id,
        role_id=role_id,
        invited_by=invited_by,
        email=email,
        token=generate_invitation_token(),
        status=InvitationStatus.PENDING,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(
                days=INVITATION_EXPIRY_DAYS
            )
        ),
    )

    return create_invitation(
        db,
        invitation,
    )



def get_invitation(
    db: Session,
    token: str,
) -> OrganizationInvitation:
    """
    Retrieve an invitation by token.
    """

    invitation = get_invitation_by_token(
        db,
        token,
    )

    if not invitation:
        raise ValueError(
            "Invitation not found"
        )

    return invitation



def accept_invitation(
    db: Session,
    token: str,
    user_id: UUID,
) -> OrganizationMember:
    """
    Accept an organization invitation.
    """

    invitation = get_invitation_by_token(
        db,
        token,
    )

    if not invitation:
        raise ValueError(
            "Invitation not found"
        )


    if invitation.status != InvitationStatus.PENDING:
        raise ValueError(
            "Invitation is no longer active"
        )


    if invitation.expires_at < datetime.now(timezone.utc):

        update_invitation_status(
            db,
            invitation,
            InvitationStatus.EXPIRED,
        )

        raise ValueError(
            "Invitation has expired"
        )


    existing_member = get_member(
        db,
        invitation.organization_id,
        user_id,
    )

    if existing_member:
        raise ValueError(
            "User is already a member of this organization"
        )


    role = get_role_by_id(
        db,
        invitation.role_id,
    )

    if not role:
        raise ValueError(
            "Invitation role not found"
        )


    membership = OrganizationMember(
        organization_id=invitation.organization_id,
        user_id=user_id,
        role=role.name,
    )


    db.add(membership)


    invitation.status = InvitationStatus.ACCEPTED

    invitation.accepted_at = datetime.now(
        timezone.utc
    )


    db.commit()

    db.refresh(membership)


    return membership



def cancel_invitation(
    db: Session,
    invitation_id: UUID,
) -> bool:
    """
    Cancel an organization invitation.
    """

    invitation = get_invitation_by_id(
        db,
        invitation_id,
    )

    if not invitation:
        raise ValueError(
            "Invitation not found"
        )


    if invitation.status != InvitationStatus.PENDING:
        raise ValueError(
            "Only pending invitations can be cancelled"
        )


    update_invitation_status(
        db,
        invitation,
        InvitationStatus.CANCELLED,
    )


    return True



def remove_invitation(
    db: Session,
    invitation_id: UUID,
) -> bool:
    """
    Delete an invitation.
    """

    invitation = get_invitation_by_id(
        db,
        invitation_id,
    )

    if not invitation:
        raise ValueError(
            "Invitation not found"
        )


    return delete_invitation(
        db,
        invitation,
    )