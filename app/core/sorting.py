from sqlalchemy import asc
from sqlalchemy import desc


def apply_sorting(
    query,
    sort_by: str | None,
    sort_order: str = "asc",
    allowed_fields: dict | None = None,
):
    """
    Apply sorting to a SQLAlchemy query.

    Only fields present in allowed_fields
    can be used for sorting.
    """

    if not sort_by or not allowed_fields:
        return query

    column = allowed_fields.get(sort_by)

    if column is None:
        return query

    if sort_order.lower() == "desc":
        return query.order_by(
            desc(column)
        )

    return query.order_by(
        asc(column)
    )