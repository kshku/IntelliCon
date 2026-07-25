import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://intellicon:intellicon@localhost:5432/intellicon",
)
