from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)


def get_organization_by_id(
    db: Session,
    organization_id,
):
    return (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )


def get_organization_by_slug(
    db: Session,
    slug: str,
):
    return (
        db.query(Organization)
        .filter(
            Organization.slug == slug
        )
        .first()
    )


def get_organizations(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
):

    query = db.query(Organization)

    if search:
        query = query.filter(
            Organization.name.ilike(
                f"%{search}%"
            )
        )

    return (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_organizations(
    db: Session,
    search: str | None = None,
):

    query = db.query(Organization)

    if search:
        query = query.filter(
            Organization.name.ilike(
                f"%{search}%"
            )
        )

    return query.count()


def create_organization(
    db: Session,
    organization_data: OrganizationCreate,
):

    organization = Organization(
        name=organization_data.name,
        slug=organization_data.slug,
        description=organization_data.description,
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


def update_organization(
    db: Session,
    organization: Organization,
    organization_data: OrganizationUpdate,
):

    update_data = organization_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            organization,
            field,
            value,
        )

    db.commit()
    db.refresh(organization)

    return organization


def delete_organization(
    db: Session,
    organization: Organization,
):

    db.delete(organization)
    db.commit()

    return True