from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.notification import (
    create_notification,
    get_notification,
    list_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification,
    delete_read_notifications,
)

from app.schemas.notification import (
    NotificationCreate,
)


def create_new_notification(
    db: Session,
    data: NotificationCreate,
):
    """
    Create a new notification.
    """

    return create_notification(
        db,
        user_id=data.user_id,
        type=data.type,
        title=data.title,
        message=data.message,
    )


def get_user_notifications(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 10,
    is_read: bool | None = None,
):
    """
    Retrieve notifications belonging to a user.
    """

    total, notifications = list_notifications(
        db,
        user_id,
        skip,
        limit,
        is_read,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "notifications": notifications,
    }


def get_user_notification(
    db: Session,
    notification_id: UUID,
    user_id: UUID,
):
    """
    Retrieve one notification belonging to a user.
    """

    notification = get_notification(
        db,
        notification_id,
    )

    if not notification:
        raise ValueError(
            "Notification not found"
        )

    if notification.user_id != user_id:
        raise ValueError(
            "You can only access your own notifications"
        )

    return notification


def mark_user_notification_as_read(
    db: Session,
    notification_id: UUID,
    user_id: UUID,
):
    """
    Mark one of the user's notifications as read.
    """

    notification = get_user_notification(
        db,
        notification_id,
        user_id,
    )

    if notification.is_read:
        return notification

    return mark_notification_as_read(
        db,
        notification,
    )


def mark_user_notifications_as_read(
    db: Session,
    user_id: UUID,
):
    """
    Mark all notifications belonging to a user as read.
    """

    count = mark_all_notifications_as_read(
        db,
        user_id,
    )

    return {
        "message": (
            "Notifications marked as read successfully"
        ),
        "updated": count,
    }


def remove_user_notification(
    db: Session,
    notification_id: UUID,
    user_id: UUID,
):
    """
    Delete one of the user's notifications.
    """

    notification = get_user_notification(
        db,
        notification_id,
        user_id,
    )

    return delete_notification(
        db,
        notification,
    )


def remove_read_notifications(
    db: Session,
    user_id: UUID,
):
    """
    Delete all read notifications belonging
    to a user.
    """

    count = delete_read_notifications(
        db,
        user_id,
    )

    return {
        "message": (
            "Read notifications deleted successfully"
        ),
        "deleted": count,
    }