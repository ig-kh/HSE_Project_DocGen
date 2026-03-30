from fastapi import Request
from fastapi.responses import JSONResponse

from utils.exceptions import DocGenError


async def docgen_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, DocGenError):
        return JSONResponse(
            status_code=400,
            content={"error": exc.__class__.__name__, "message": exc.message},
        )

    return JSONResponse(
        status_code=500, content={"error": "InternalServerError", "message": str(exc)}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content={"error": "InternalServerError", "message": str(exc)}
    )
