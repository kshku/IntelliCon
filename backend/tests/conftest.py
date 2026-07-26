import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://intellicon:intellicon@localhost:5432/intellicon",
)

from app.models.user import User


def _make_test_user():
    return User(
        user_id=1,
        employee_id=1001,
        username="testuser",
        role="admin",
        active=True,
    )


MOCK_USER = _make_test_user()
