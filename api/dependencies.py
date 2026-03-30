from functools import lru_cache

from api.config import settings
from db.session import SessionLocal
from pipelines.contract_generation_pipeline import ContractGenerationPipeline


@lru_cache()
def get_pipeline():
    pipeline = ContractGenerationPipeline(
        model_path=settings.MODEL_PATH,
        template_path=settings.BASE_CONTRACT_TEMPLATE_PATH,
    )
    return pipeline


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
