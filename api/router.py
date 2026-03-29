from fastapi import APIRouter
from api.endpoints import generate

router = APIRouter()

router.include_router(
    generate.router,
    prefix="/contracts",
    tags=["contracts"],
)
