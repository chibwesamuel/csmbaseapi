from sqlalchemy.orm import Session
from sqlalchemy import or_

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

def get_organization_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(Organization)
        .filter(
            Organization.email == email
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
        or_(
            Organization.name.ilike(f"%{search}%"),
            Organization.slug.ilike(f"%{search}%"),
            Organization.description.ilike(f"%{search}%"),
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
        or_(
            Organization.name.ilike(f"%{search}%"),
            Organization.slug.ilike(f"%{search}%"),
            Organization.description.ilike(f"%{search}%"),
        )
    )

    return query.count()


def create_organization(
    db: Session,
    organization_data: OrganizationCreate,
):

    organization = Organization(
        **organization_data.model_dump()
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