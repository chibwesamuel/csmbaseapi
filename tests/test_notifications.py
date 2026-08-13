import uuid

from app.models.notification import Notification

# ==========================================================
# Helpers
# ==========================================================

def create_notification(
    db,
    user_id,
    *,
    notification_type="system",
    title="Test Notification",
    message="This is a test notification.",
    is_read=False,
):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        is_read=is_read,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# ==========================================================
# List Notifications
# ==========================================================

def test_user_can_list_notifications(
    client,
    db,
    notification_user,
    notification_headers,
):
    create_notification(
        db,
        notification_user.id,
    )

    response = client.get(
        "/api/v1/notifications",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert len(data["notifications"]) == 1

    notification = data["notifications"][0]

    assert notification["user_id"] == str(notification_user.id)
    assert notification["title"] == "Test Notification"
    assert notification["is_read"] is False


def test_user_can_filter_unread_notifications(
    client,
    db,
    notification_user,
    notification_headers,
):
    create_notification(
        db,
        notification_user.id,
        title="Unread",
        is_read=False,
    )

    create_notification(
        db,
        notification_user.id,
        title="Read",
        is_read=True,
    )

    response = client.get(
        "/api/v1/notifications?is_read=false",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["title"] == "Unread"


def test_user_can_filter_read_notifications(
    client,
    db,
    notification_user,
    notification_headers,
):
    create_notification(
        db,
        notification_user.id,
        title="Unread",
        is_read=False,
    )

    create_notification(
        db,
        notification_user.id,
        title="Read",
        is_read=True,
    )

    response = client.get(
        "/api/v1/notifications?is_read=true",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["title"] == "Read"


def test_user_only_sees_own_notifications(
    client,
    db,
    notification_user,
    normal_user,
    notification_headers,
):
    create_notification(
        db,
        notification_user.id,
        title="My Notification",
    )

    create_notification(
        db,
        normal_user.id,
        title="Other User Notification",
    )

    response = client.get(
        "/api/v1/notifications",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["notifications"][0]["title"] == "My Notification"


# ==========================================================
# Retrieve Single Notification
# ==========================================================

def test_user_can_get_own_notification(
    client,
    db,
    notification_user,
    notification_headers,
):
    notification = create_notification(
        db,
        notification_user.id,
    )

    response = client.get(
        f"/api/v1/notifications/{notification.id}",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(notification.id)
    assert data["user_id"] == str(notification_user.id)


def test_user_cannot_get_another_users_notification(
    client,
    db,
    notification_user,
    normal_user,
    notification_headers,
):
    notification = create_notification(
        db,
        normal_user.id,
    )

    response = client.get(
        f"/api/v1/notifications/{notification.id}",
        headers=notification_headers,
    )

    assert response.status_code == 404
    assert response.json()["message"] == "You can only access your own notifications"


def test_get_nonexistent_notification_returns_404(
    client,
    notification_headers,
):
    notification_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/notifications/{notification_id}",
        headers=notification_headers,
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Notification not found"


# ==========================================================
# Mark As Read
# ==========================================================

def test_user_can_mark_notification_as_read(
    client,
    db,
    notification_user,
    notification_headers,
):
    notification = create_notification(
        db,
        notification_user.id,
        is_read=False,
    )

    response = client.patch(
        f"/api/v1/notifications/{notification.id}/read",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_read"] is True
    assert data["read_at"] is not None


def test_marking_already_read_notification_is_safe(
    client,
    db,
    notification_user,
    notification_headers,
):
    notification = create_notification(
        db,
        notification_user.id,
        is_read=True,
    )

    response = client.patch(
        f"/api/v1/notifications/{notification.id}/read",
        headers=notification_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_user_cannot_mark_another_users_notification_as_read(
    client,
    db,
    notification_user,
    normal_user,
    notification_headers,
):
    notification = create_notification(
        db,
        normal_user.id,
    )

    response = client.patch(
        f"/api/v1/notifications/{notification.id}/read",
        headers=notification_headers,
    )

    assert response.status_code == 404

    db.refresh(notification)

    assert notification.is_read is False


def test_user_can_mark_all_notifications_as_read(
    client,
    db,
    notification_user,
    notification_headers,
):
    create_notification(
        db,
        notification_user.id,
        title="First",
    )

    create_notification(
        db,
        notification_user.id,
        title="Second",
    )

    create_notification(
        db,
        notification_user.id,
        title="Already Read",
        is_read=True,
    )

    response = client.patch(
        "/api/v1/notifications/read-all",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["updated"] == 2

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == notification_user.id)
        .all()
    )

    assert all(notification.is_read for notification in notifications)


# ==========================================================
# Delete Notifications
# ==========================================================

def test_user_can_delete_own_notification(
    client,
    db,
    notification_user,
    notification_headers,
):
    notification = create_notification(
        db,
        notification_user.id,
    )

    response = client.delete(
        f"/api/v1/notifications/{notification.id}",
        headers=notification_headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Notification deleted successfully"

    deleted = (
        db.query(Notification)
        .filter(Notification.id == notification.id)
        .first()
    )

    assert deleted is None


def test_user_cannot_delete_another_users_notification(
    client,
    db,
    notification_user,
    normal_user,
    notification_headers,
):
    notification = create_notification(
        db,
        normal_user.id,
    )

    response = client.delete(
        f"/api/v1/notifications/{notification.id}",
        headers=notification_headers,
    )

    assert response.status_code == 404

    existing = (
        db.query(Notification)
        .filter(Notification.id == notification.id)
        .first()
    )

    assert existing is not None


def test_delete_nonexistent_notification_returns_404(
    client,
    notification_headers,
):
    notification_id = uuid.uuid4()

    response = client.delete(
        f"/api/v1/notifications/{notification_id}",
        headers=notification_headers,
    )

    assert response.status_code == 404


def test_user_can_delete_all_read_notifications(
    client,
    db,
    notification_user,
    notification_headers,
):
    create_notification(
        db,
        notification_user.id,
        title="Read 1",
        is_read=True,
    )

    create_notification(
        db,
        notification_user.id,
        title="Read 2",
        is_read=True,
    )

    create_notification(
        db,
        notification_user.id,
        title="Unread",
        is_read=False,
    )

    response = client.delete(
        "/api/v1/notifications/read",
        headers=notification_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["deleted"] == 2

    remaining = (
        db.query(Notification)
        .filter(Notification.user_id == notification_user.id)
        .all()
    )

    assert len(remaining) == 1
    assert remaining[0].title == "Unread"


def test_delete_read_notifications_does_not_delete_other_users_notifications(
    client,
    db,
    notification_user,
    normal_user,
    notification_headers,
):
    create_notification(
        db,
        notification_user.id,
        title="My Read",
        is_read=True,
    )

    other_notification = create_notification(
        db,
        normal_user.id,
        title="Other Read",
        is_read=True,
    )

    response = client.delete(
        "/api/v1/notifications/read",
        headers=notification_headers,
    )

    assert response.status_code == 200
    assert response.json()["deleted"] == 1

    existing = (
        db.query(Notification)
        .filter(
            Notification.id
            == other_notification.id
        )
        .first()
    )

    assert existing is not None
