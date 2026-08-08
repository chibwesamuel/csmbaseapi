from typing import Any, Optional

from fastapi.responses import JSONResponse


def success_response(
    message: str,
    data: Any = None,
    meta: Optional[dict] = None,
    status_code: int = 200,
) -> JSONResponse:
    """
    Standard successful API response.
    """

    content = {
        "success": True,
        "message": message,
        "data": data,
    }

    if meta is not None:
        content["meta"] = meta

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def error_response(
    message: str,
    status_code: int,
    errors: Any = None,
) -> JSONResponse:
    """
    Standard error API response.
    """

    content = {
        "success": False,
        "message": message,
    }

    if errors is not None:
        content["errors"] = errors

    return JSONResponse(
        status_code=status_code,
        content=content,
    )