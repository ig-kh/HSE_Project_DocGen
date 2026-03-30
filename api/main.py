from fastapi import FastAPI

from api.config import settings
from api.router import router
from utils.exceptions import DocGenError
from utils.error_handlers import docgen_exception_handler, generic_exception_handler


def create_app() -> FastAPI:
    app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)

    app.include_router(router)

    app.add_exception_handler(DocGenError, docgen_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    return app


app = create_app()
