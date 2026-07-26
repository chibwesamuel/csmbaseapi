from typing import Annotated

from fastapi import Query


PageParam = Annotated[
    int,
    Query(
        default=1,
        ge=1,
        description="Page number",
    ),
]

PageSizeParam = Annotated[
    int,
    Query(
        default=10,
        ge=1,
        le=100,
        description="Items per page",
    ),
]

SearchParam = Annotated[
    str | None,
    Query(
        default=None,
        description="Search term",
    ),
]

SortByParam = Annotated[
    str | None,
    Query(
        default=None,
        description="Field to sort by",
    ),
]

SortOrderParam = Annotated[
    str,
    Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order",
    ),
]