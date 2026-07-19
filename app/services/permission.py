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
) -> PaginatedPermissionsResponse:
    permissions = get_permissions(
        db,
        skip,
        limit,
        search,
    )

    total = count_permissions(
        db,
        search,
    )

    return PaginatedPermissionsResponse(
        total=total,
        skip=skip,
        limit=limit,
        permissions=permissions,
    )


def get_permission(
    db: Session,
    permission_id,
):
    return get_permission_by_id(
        db,
        permission_id,
    )


def create_new_permission(
    db: Session,
    permission_data: PermissionCreate,
):
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
):
    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if not permission:
        return None

    return update_permission_repository(
        db,
        permission,
        permission_data,
    )


def delete_existing_permission(
    db: Session,
    permission_id,
):
    permission = get_permission_by_id(
        db,
        permission_id,
    )

    if not permission:
        return False

    return delete_permission_repository(
        db,
        permission,
    )