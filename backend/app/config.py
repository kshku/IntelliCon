from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM Provider
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o"
    LLM_API_KEY: str = ""

    # PostgreSQL
    DATABASE_URL: str = "postgresql://intellicon:intellicon@localhost:5432/intellicon"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "intellicon"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Agent
    AGENT_MAX_ITERATIONS: int = 10
    SQL_QUERY_TIMEOUT: int = 30
    SQL_MAX_ROWS: int = 1000

    # Auth
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # Initial User Seed Passwords (configurable via environment/dotenv)
    SEED_ADMIN_PASSWORD: str = "admin123"
    SEED_INVESTIGATOR_PASSWORD: str = "inv123"
    SEED_SUPERVISOR_PASSWORD: str = "sup123"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
