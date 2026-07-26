from math import ceil

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
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> PaginatedRolesResponse:
    """
    Return a paginated list of roles
    with search and sorting.
    """

    roles = get_roles(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total = count_roles(
        db=db,
        search=search,
    )

    page = (
        skip // limit
    ) + 1

    total_pages = (
        ceil(total / limit)
        if total > 0
        else 1
    )

    return PaginatedRolesResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
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