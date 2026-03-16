from functools import lru_cache
from app.db.session import SessionLocal
from app.pipelines.contract_generation_pipeline import ContractGenerationPipeline


@lru_cache()
def get_pipeline():
    pipeline = ContractGenerationPipeline(
        model_path="models/qwen3-8b-q4.gguf", # указать потом корректный путь 
        template_path="templates/base_contract.docx" # аналогично
    )
    return pipeline

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
