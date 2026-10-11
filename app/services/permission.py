from math import ceil

from sqlalchemy.orm import Session

from app.repositories.permission import (
    count_permissions,
    create_permission as create_permission_repository,
    delete_permission as delete_permission_repository,
    get_permission_by_id,
    get_permission_by_name,
    get_permissions,
    update_permission as update_permission_repository,
)

from app.core.exceptions import Forbidden
from app.core.system_permissions import SYSTEM_PERMISSION_NAMES
from app.models.user import User

from app.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PaginatedPermissionsResponse,
)


def list_permissions(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> PaginatedPermissionsResponse:
    """
    Return a paginated list of permissions
    with search and sorting.
    """

    permissions = get_permissions(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total = count_permissions(
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

    return PaginatedPermissionsResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        permissions=permissions,
    )


def get_permission(
    db: Session,
    permission_id,
):
    """
    Return a permission by its ID.
    """

    return get_permission_by_id(
        db,
        permission_id,
    )


def create_new_permission(
    db: Session,
    permission_data: PermissionCreate,
):
    """
    Create a new permission.
    """

    existing = get_permission_by_name(
        db,
        permission_data.name,
    )

    if existing:
        return None

    return create_permission_repository(
        db,
        permission_data,
    )


def update_existing_permission(
    db: Session,
    permission_id,
    permission_data: PermissionUpdate,
    current_user: User,
):
    """
    Update an existing permission.
    """

    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if not permission:
        return None

    if (
        permission.name in SYSTEM_PERMISSION_NAMES
        and not current_user.is_superuser
    ):
        raise Forbidden(
            "Only a superuser can modify system permissions"
        )

    return update_permission_repository(
        db,
        permission,
        permission_data,
    )


def delete_existing_permission(
    db: Session,
    permission_id,
    current_user: User,
):
    """
    Delete an existing permission.
    """

    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if not permission:
        return False

    if (
        permission.name in SYSTEM_PERMISSION_NAMES
        and not current_user.is_superuser
    ):
        raise Forbidden(
            "Only a superuser can delete system permissions"
        )

    return delete_permission_repository(
        db,
        permission,
    )