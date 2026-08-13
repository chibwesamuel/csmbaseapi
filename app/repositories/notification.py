from datetime import datetime, timezone

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    **kwargs,
) -> Notification:
    """
    Create a notification.
    """

    notification = Notification(**kwargs)

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notification(
    db: Session,
    notification_id: UUID,
) -> Notification | None:
    """
    Retrieve a single notification.
    """

    return (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
        )
        .first()
    )


def list_notifications(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 10,
    is_read: bool | None = None,
):
    """
    List notifications belonging to a user.
    """

    query = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
        )
    )

    if is_read is not None:
        query = query.filter(
            Notification.is_read == is_read,
        )

    query = query.order_by(
        Notification.created_at.desc()
    )

    total = query.count()

    notifications = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, notifications


def mark_notification_as_read(
    db: Session,
    notification: Notification,
) -> Notification:
    """
    Mark a notification as read.
    """


    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: UUID,
) -> int:
    """
    Mark all unread notifications belonging
    to a user as read.

    Returns the number of notifications updated.
    """

    from datetime import datetime, timezone

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for notification in notifications:
        notification.is_read = True
        notification.read_at = now

    db.commit()

    return len(notifications)


def delete_notification(
    db: Session,
    notification: Notification,
) -> bool:
    """
    Delete a notification.
    """

    db.delete(notification)
    db.commit()

    return True


def delete_read_notifications(
    db: Session,
    user_id: UUID,
) -> int:
    """
    Delete all read notifications belonging
    to a user.

    Returns the number of notifications deleted.
    """

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(True),
        )
        .all()
    )

    count = len(notifications)

    for notification in notifications:
        db.delete(notification)

    db.commit()

    return count