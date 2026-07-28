from typing import Annotated

from fastapi import Query


PageParam = Annotated[
    int,
    Query(
        ge=1,
        description="Page number",
    ),
]


PageSizeParam = Annotated[
    int,
    Query(
        ge=1,
        le=100,
        description="Number of records per page",
    ),
]


SearchParam = Annotated[
    str | None,
    Query(
        min_length=1,
        description="Search term",
    ),
]


SortByParam = Annotated[
    str | None,
    Query(
        description="Field to sort by",
    ),
]


SortOrderParam = Annotated[
    str,
    Query(
        pattern="^(asc|desc)$",
        description="Sort direction",
    ),
]