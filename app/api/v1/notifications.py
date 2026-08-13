from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.permissions import require_permission

from app.models.user import User

from app.schemas.notification import (
    NotificationResponse,
    PaginatedNotificationsResponse,
)

from app.services.notification import (
    get_user_notifications,
    get_user_notification,
    mark_user_notification_as_read,
    mark_user_notifications_as_read,
    remove_user_notification,
    remove_read_notifications,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=PaginatedNotificationsResponse,
)
def list_notifications_endpoint(
    skip: int = 0,
    limit: int = 10,
    is_read: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.view")
    ),
):
    """
    List the current user's notifications.
    """

    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 100",
        )

    return get_user_notifications(
        db,
        current_user.id,
        skip,
        limit,
        is_read,
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification_endpoint(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.view")
    ),
):
    """
    Retrieve one notification.
    """

    try:
        return get_user_notification(
            db,
            notification_id,
            current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_read_endpoint(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.update")
    ),
):
    """
    Mark one notification as read.
    """

    try:
        return mark_user_notification_as_read(
            db,
            notification_id,
            current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "/read-all",
)
def mark_all_notifications_read_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.update")
    ),
):
    """
    Mark all notifications as read.
    """

    return mark_user_notifications_as_read(
        db,
        current_user.id,
    )


@router.delete(
    "/read",
)
def delete_read_notifications_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.delete")
    ),
):
    """
    Delete all read notifications.
    """

    return remove_read_notifications(
        db,
        current_user.id,
    )


@router.delete(
    "/{notification_id}",
)
def delete_notification_endpoint(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.delete")
    ),
):
    """
    Delete one notification.
    """

    try:
        remove_user_notification(
            db,
            notification_id,
            current_user.id,
        )

        return {
            "message": (
                "Notification deleted successfully"
            )
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )