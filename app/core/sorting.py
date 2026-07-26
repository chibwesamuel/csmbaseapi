from sqlalchemy import asc
from sqlalchemy import desc


def apply_sorting(
    query,
    model,
    sort_by: str | None,
    sort_order: str = "asc",
):
    """
    Apply dynamic sorting to a SQLAlchemy query.

    Invalid fields are ignored gracefully.
    """

    if not sort_by:
        return query

    column = getattr(
        model,
        sort_by,
        None,
    )

    if column is None:
        return query

    if sort_order.lower() == "desc":
        return query.order_by(
            desc(column)
        )

    return query.order_by(
        asc(column)
    )