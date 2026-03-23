from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "DocGen"
    APP_VERSION: str = "0.1.0"
    OPENAI_API_KEY: str | None = None
    MODEL_NAME: str = "gpt-4.1"
    DOC_TEMPLATE_PATH: str = "templates/"
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
