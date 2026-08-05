from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember


def create_project_member(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    role: str = "contributor",
):
    """
    Add a user to a project.
    """

    membership = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership


def get_project_member(
    db: Session,
    project_id: UUID,
    user_id: UUID,
):
    """
    Retrieve a project membership.
    """

    return (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )


def list_project_members(
    db: Session,
    project_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    List project members.
    """

    query = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id
        )
    )

    total = query.count()

    members = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, members


def update_project_member(
    db: Session,
    membership: ProjectMember,
    role: str,
):
    """
    Update project member role.
    """

    membership.role = role

    db.commit()
    db.refresh(membership)

    return membership


def delete_project_member(
    db: Session,
    membership: ProjectMember,
):
    """
    Remove project member.
    """

    db.delete(membership)
    db.commit()

    return True