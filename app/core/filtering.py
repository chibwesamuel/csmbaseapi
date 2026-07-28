def apply_boolean_filter(
    query,
    column,
    value: bool | None,
):
    """
    Apply an optional boolean filter.

    Example:
        query = apply_boolean_filter(
            query,
            User.is_active,
            is_active,
        )
    """

    if value is None:
        return query

    return query.filter(
        column == value
    )


def apply_exact_filter(
    query,
    column,
    value,
):
    """
    Apply an optional exact-match filter.
    """

    if value is None:
        return query

    return query.filter(
        column == value
    )