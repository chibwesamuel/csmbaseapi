from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.dependencies.organization import (
    get_current_organization,
)

from app.dependencies.organization_permissions import (
    get_membership,
    require_organization_owner,
    require_organization_admin,
    require_organization_member,
)

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember


def create_query_mock(result):
    """
    Create a mock SQLAlchemy query chain.
    """

    query = MagicMock()

    query.filter.return_value = query
    query.first.return_value = result

    return query


def create_user():
    user = MagicMock()
    user.id = uuid4()

    return user


def create_organization():
    organization = Organization(
        name="Test Organization",
        slug="test-org",
    )

    organization.id = uuid4()

    return organization


def create_membership(
    role="member",
):
    membership = OrganizationMember(
        organization_id=uuid4(),
        user_id=uuid4(),
        role=role,
    )

    membership.id = uuid4()

    return membership


# ---------------------------------------------------------
# get_current_organization
# ---------------------------------------------------------


def test_get_current_organization_success():

    organization = create_organization()
    user = create_user()

    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role="member",
    )

    db = MagicMock()

    db.query.side_effect = [
        create_query_mock(membership),
        create_query_mock(organization),
    ]

    result = get_current_organization(
        organization_id=organization.id,
        db=db,
        current_user=user,
    )

    assert result == organization


def test_get_current_organization_without_membership():

    user = create_user()

    db = MagicMock()

    db.query.return_value = create_query_mock(None)

    with pytest.raises(HTTPException) as exc:

        get_current_organization(
            organization_id=uuid4(),
            db=db,
            current_user=user,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "User does not belong to this organization"
    )


def test_get_current_organization_missing_organization():

    user = create_user()

    organization_id = uuid4()

    membership = OrganizationMember(
        organization_id=organization_id,
        user_id=user.id,
        role="member",
    )

    db = MagicMock()

    db.query.side_effect = [
        create_query_mock(membership),
        create_query_mock(None),
    ]

    with pytest.raises(HTTPException) as exc:

        get_current_organization(
            organization_id=organization_id,
            db=db,
            current_user=user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Organization not found"
    )


# ---------------------------------------------------------
# get_membership
# ---------------------------------------------------------


def test_get_membership_success():

    organization = create_organization()
    user = create_user()

    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role="member",
    )

    db = MagicMock()

    db.query.return_value = create_query_mock(
        membership
    )

    result = get_membership(
        organization=organization,
        current_user=user,
        db=db,
    )

    assert result == membership


def test_get_membership_missing():

    organization = create_organization()
    user = create_user()

    db = MagicMock()

    db.query.return_value = create_query_mock(None)

    with pytest.raises(HTTPException) as exc:

        get_membership(
            organization=organization,
            current_user=user,
            db=db,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == (
        "Organization membership required"
    )


# ---------------------------------------------------------
# require_organization_owner
# ---------------------------------------------------------


def test_require_organization_owner_success():

    membership = create_membership(
        "owner"
    )

    result = require_organization_owner(
        membership
    )

    assert result == membership


@pytest.mark.parametrize(
    "role",
    [
        "admin",
        "member",
    ],
)
def test_require_organization_owner_failure(role):

    membership = create_membership(role)

    with pytest.raises(HTTPException) as exc:

        require_organization_owner(
            membership
        )

    assert exc.value.status_code == 403


# ---------------------------------------------------------
# require_organization_admin
# ---------------------------------------------------------


@pytest.mark.parametrize(
    "role",
    [
        "owner",
        "admin",
    ],
)
def test_require_organization_admin_success(role):

    membership = create_membership(role)

    result = require_organization_admin(
        membership
    )

    assert result == membership


def test_require_organization_admin_failure():

    membership = create_membership(
        "member"
    )

    with pytest.raises(HTTPException) as exc:

        require_organization_admin(
            membership
        )

    assert exc.value.status_code == 403


# ---------------------------------------------------------
# require_organization_member
# ---------------------------------------------------------


def test_require_organization_member():

    membership = create_membership()

    result = require_organization_member(
        membership
    )

    assert result == membership