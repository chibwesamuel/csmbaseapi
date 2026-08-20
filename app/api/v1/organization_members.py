from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.organization_permissions import (
    require_organization_admin,
    require_organization_member,
)

from app.models.organization import Organization
from app.models.user import User
from app.models.role import Role

from app.schemas.organization_member import (
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    OrganizationMemberResponse,
    PaginatedOrganizationMembersResponse,
)

from app.services.organization_member import (
    list_members,
    add_member,
    change_member_role,
    remove_member,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organization Members"],
)


# =========================================================
# HELPERS
# =========================================================

def check_organization_exists(
    db: Session,
    organization_id: UUID,
):
    """
    Ensure the organization exists.
    """

    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization


def get_role_by_name(
    db: Session,
    role_name: str,
):
    """
    Resolve an organization role name into
    the corresponding Role model.
    """

    role = (
        db.query(Role)
        .filter(
            Role.name == role_name.lower()
        )
        .first()
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return role


# =========================================================
# LIST ORGANIZATION MEMBERS
# =========================================================

@router.get(
    "/{organization_id}/members",
    response_model=PaginatedOrganizationMembersResponse,
)
def get_organization_members(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    membership=Depends(
        require_organization_member
    ),
):
    """
    List all members belonging to an organization.

    Any authenticated member of the organization
    may view its members.
    """

    check_organization_exists(
        db,
        organization_id,
    )

    return list_members(
        db,
        organization_id,
        skip,
        limit,
    )


# =========================================================
# ADD ORGANIZATION MEMBER
# =========================================================

@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization_member(
    organization_id: UUID,
    member_data: OrganizationMemberCreate,
    db: Session = Depends(get_db),
    membership=Depends(
        require_organization_admin
    ),
):
    """
    Add a user to an organization.

    Only organization owners and administrators
    may add members.
    """

    check_organization_exists(
        db,
        organization_id,
    )

    role = get_role_by_name(
        db,
        member_data.role,
    )

    try:
        return add_member(
            db,
            organization_id,
            member_data.user_id,
            role.id,
        )

    except ValueError as error:

        message = str(error)

        if message in (
            "Organization not found",
            "User not found",
            "Role not found",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == (
            "User is already a member of this organization"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# =========================================================
# UPDATE ORGANIZATION MEMBER ROLE
# =========================================================

@router.patch(
    "/{organization_id}/members/{user_id}",
    response_model=OrganizationMemberResponse,
)
def update_organization_member(
    organization_id: UUID,
    user_id: UUID,
    member_data: OrganizationMemberUpdate,
    db: Session = Depends(get_db),
    membership=Depends(
        require_organization_admin
    ),
):
    """
    Update an organization member's role.

    Only organization owners and administrators
    may change member roles.
    """

    check_organization_exists(
        db,
        organization_id,
    )

    role = None

    if member_data.role is not None:
        role = get_role_by_name(
            db,
            member_data.role,
        )

    try:
        return change_member_role(
            db,
            organization_id,
            user_id,
            role.id if role else None,
        )

    except ValueError as error:

        message = str(error)

        if message in (
            "Membership not found",
            "Role not found",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# =========================================================
# REMOVE ORGANIZATION MEMBER
# =========================================================

@router.delete(
    "/{organization_id}/members/{user_id}",
)
def delete_organization_member(
    organization_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    membership=Depends(
        require_organization_admin
    ),
):
    """
    Remove a user from an organization.

    Only organization owners and administrators
    may remove members.
    """

    check_organization_exists(
        db,
        organization_id,
    )

    try:
        remove_member(
            db,
            organization_id,
            user_id,
        )

        return {
            "message": "Member removed successfully"
        }

    except ValueError as error:

        message = str(error)

        if message == "Membership not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )