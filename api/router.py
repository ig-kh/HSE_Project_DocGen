from fastapi import APIRouter

from api.config import settings
from api.endpoints import generate

router = APIRouter()

router.include_router(
    generate.router,
    prefix=settings.CONTRACTS_ROUTE_PREFIX,
    tags=[settings.CONTRACTS_ROUTE_TAG],
)
