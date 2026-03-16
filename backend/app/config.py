from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "DocGen"
    APP_VERSION: str = "0.1.0"

    OPENAI_API_KEY: str

    MODEL_NAME: str = "gpt-4.1"

    DOC_TEMPLATE_PATH: str = "templates/"

    class Config:
        env_file = ".env"


settings = Settings()
