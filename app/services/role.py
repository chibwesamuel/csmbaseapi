from sqlalchemy.orm import Session

from app.repositories.role import (
    count_roles,
    create_role as create_role_repository,
    delete_role as delete_role_repository,
    get_role_by_id,
    get_role_by_name,
    get_roles,
    update_role as update_role_repository,
)

from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    PaginatedRolesResponse,
)


def list_roles(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
) -> PaginatedRolesResponse:
    """
    Return a paginated list of roles.
    """

    roles = get_roles(
        db,
        skip,
        limit,
        search,
    )

    total = count_roles(
        db,
        search,
    )

    return PaginatedRolesResponse(
        total=total,
        skip=skip,
        limit=limit,
        roles=roles,
    )


def get_role(
    db: Session,
    role_id,
):
    """
    Return a role by its ID.
    """

    return get_role_by_id(
        db,
        role_id,
    )


def create_new_role(
    db: Session,
    role_data: RoleCreate,
):
    """
    Create a new role.
    """

    existing = get_role_by_name(
        db,
        role_data.name,
    )

    if existing:
        return None

    return create_role_repository(
        db,
        role_data,
    )


def update_existing_role(
    db: Session,
    role_id,
    role_data: RoleUpdate,
):
    """
    Update an existing role.
    """

    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        return None

    return update_role_repository(
        db,
        role,
        role_data,
    )


def delete_existing_role(
    db: Session,
    role_id,
):
    """
    Delete a role.
    """

    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        return False

    return delete_role_repository(
        db,
        role,
    )