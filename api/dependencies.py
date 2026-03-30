from functools import lru_cache
from db.session import SessionLocal
from pipelines.contract_generation_pipeline import ContractGenerationPipeline


@lru_cache()
def get_pipeline():
    pipeline = ContractGenerationPipeline(
        model_path="models/Qwen3-4B-Q4_K_M.gguf",  # указать потом корректный путь
        template_path="templates/base_contract.docx",  # аналогично
    )
    return pipeline


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
