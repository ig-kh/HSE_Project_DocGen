from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "DocGen"
    API_TITLE: str = "DocGen API"
    APP_VERSION: str = "0.1.0"
    API_VERSION: str = "0.1"

    CONTRACTS_ROUTE_PREFIX: str = "/contracts"
    CONTRACTS_ROUTE_TAG: str = "contracts"

    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@postgres:5432/docsgen_llm"
    )

    DOC_TEMPLATE_PATH: Path = BASE_DIR / "templates"
    BASE_CONTRACT_TEMPLATE_PATH: Path = DOC_TEMPLATE_PATH / "base_contract.docx"
    MODEL_PATH: Path = BASE_DIR / "models" / "Qwen3-8B-Q4_K_M.gguf"

    DOCS_DIR: Path = BASE_DIR / "docs"
    RAW_DOC_PATH: Path = DOCS_DIR / "raw.docx"
    PROCESSED_DOC_PATH: Path = DOCS_DIR / "processed.docx"
    GENERATED_CONTRACTS_DIR: Path = BASE_DIR / "generated_contracts"

    EXTRACTOR_SYSTEM_PROMPT_PATH: Path = (
        BASE_DIR / "services" / "extractor" / "system_prompt.txt"
    )
    REPLACER_SYSTEM_PROMPT_PATH: Path = (
        BASE_DIR / "services" / "replacer" / "system_prompt.txt"
    )

    LOGGER_NAME: str = "docgen"
    LOGS_DIR: Path = BASE_DIR / "logs"
    LOG_FILE_PATH: Path = LOGS_DIR / "docgen.log"

    ENABLE_DIFF_HIGHLIGHTING: bool = True

    LLM_N_CTX: int = 12000
    LLM_N_THREADS: int = 8
    LLM_N_GPU_LAYERS: int = -1
    LLM_N_BATCH: int = 512
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.2

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
