from pydantic_settings import BaseSettings


class AnalyticsSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://intellicon:intellicon@localhost:5432/intellicon"
    REDIS_URL: str = "redis://localhost:6379/0"
    ANALYTICS_WEBHOOK_URL: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = AnalyticsSettings()
