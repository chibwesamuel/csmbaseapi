import uuid


def user_payload():

    unique = uuid.uuid4().hex[:8]

    return {
        "email": f"user_{unique}@example.com",
        "username": f"user_{unique}",
        "password": "Password123!",
        "first_name": "John",
        "last_name": "Doe",
    }


def admin_payload():

    unique = uuid.uuid4().hex[:8]

    return {
        "email": f"admin_{unique}@example.com",
        "username": f"admin_{unique}",
        "password": "Password123!",
        "first_name": "Admin",
        "last_name": "User",
    }