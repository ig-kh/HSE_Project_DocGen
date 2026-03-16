from fastapi import APIRouter
from app.api.endpoints import generate

router = APIRouter()

router.include_router(
    generate.router,
    prefix="/contracts",
    tags=["contracts"],
)
