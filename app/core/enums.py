from enum import Enum


class OrganizationRole(str, Enum):
    """
    Roles available for organization members.
    """

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"