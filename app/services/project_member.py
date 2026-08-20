from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.project import (
    get_project_by_id,
)

from app.repositories.user import (
    get_user_by_id,
)

from app.repositories.project_member import (
    create_project_member,
    get_project_member,
    list_project_members,
    update_project_member,
    delete_project_member,
    count_project_owners,
)


def add_project_member(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    role: str = "contributor",
):
    """
    Add a user to a project.
    """

    project = get_project_by_id(
        db,
        project_id,
    )

    if not project:
        raise ValueError(
            "Project not found"
        )


    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise ValueError(
            "User not found"
        )


    existing = get_project_member(
        db,
        project_id,
        user_id,
    )

    if existing:
        raise ValueError(
            "User is already a project member"
        )


    return create_project_member(
        db,
        project_id,
        user_id,
        role,
    )


def get_members(
    db: Session,
    project_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve project members.
    """

    total, members = list_project_members(
        db,
        project_id,
        skip,
        limit,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "members": members,
    }


def get_member(
    db: Session,
    project_id: UUID,
    user_id: UUID,
):
    """
    Get a specific project member.
    """

    return get_project_member(
        db,
        project_id,
        user_id,
    )


def change_member_role(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    role: str,
):
    """
    Change project member role.
    """

    membership = get_project_member(
        db,
        project_id,
        user_id,
    )

    if not membership:
        raise ValueError(
            "Project membership not found"
        )


    # Prevent removing the project owner
    if (
        membership.role == "owner"
        and role != "owner"
    ):
        owners = count_project_owners(
            db,
            project_id,
        )

        if owners <= 1:
            raise ValueError(
                "A project must have at least one owner"
            )


    return update_project_member(
        db,
        membership,
        role,
    )


def remove_member(
    db: Session,
    project_id: UUID,
    user_id: UUID,
):
    """
    Remove a project member.
    """

    membership = get_project_member(
        db,
        project_id,
        user_id,
    )

    if not membership:
        raise ValueError(
            "Project membership not found"
        )


    if membership.role == "owner":

        owners = count_project_owners(
            db,
            project_id,
        )

        if owners <= 1:
            raise ValueError(
                "Cannot remove the last owner of a project"
            )


    return delete_project_member(
        db,
        membership,
    )