from typing import Any

from fastapi.responses import JSONResponse


def success_response(
    message: str,
    data: Any = None,
    status_code: int = 200,
) -> JSONResponse:
    """
    Standard successful API response.
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
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