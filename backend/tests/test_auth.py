from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

_FAKE_HASH = "$2b$12$fakeshashedpasswordforTestingOnly00000000000000"


def _mock_user(
    user_id=1,
    employee_id=100,
    username="testuser",
    password="testpass",
    role="investigator",
    active=True,
):
    user = MagicMock()
    user.user_id = user_id
    user.employee_id = employee_id
    user.username = username
    user.password_hash = _FAKE_HASH
    user.role = role
    user.active = active
    return user


def _make_mock_session(user=None):
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    return mock_session


async def _mock_get_session():
    yield _make_mock_session(None)


def _get_client(user=None):
    from app.db.session import get_session
    from app.main import app

    if user is not None:

        async def dep():
            yield _make_mock_session(user)

        app.dependency_overrides[get_session] = dep
    else:
        app.dependency_overrides[get_session] = _mock_get_session

    return TestClient(app)


class TestLogin:
    @patch("app.api.auth.verify_password", return_value=True)
    def test_login_success(self, _mock_verify):
        user = _mock_user()
        client = _get_client(user)
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "investigator"
        assert data["username"] == "testuser"

    @patch("app.api.auth.verify_password", return_value=False)
    def test_login_wrong_password(self, _mock_verify):
        user = _mock_user()
        client = _get_client(user)
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpass"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        client = _get_client(None)
        response = client.post(
            "/auth/login",
            json={"username": "nobody", "password": "pass"},
        )
        assert response.status_code == 401

    @patch("app.api.auth.verify_password", return_value=True)
    def test_login_inactive_user(self, _mock_verify):
        user = _mock_user(active=False)
        client = _get_client(user)
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass"},
        )
        assert response.status_code == 403


class TestMe:
    def test_me_without_token(self):
        client = _get_client()
        response = client.get("/auth/me")
        assert response.status_code == 401

    @patch("app.api.auth.verify_password", return_value=True)
    def test_me_with_valid_token(self, _mock_verify):
        user = _mock_user()
        client = _get_client(user)
        login_resp = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass"},
        )
        token = login_resp.json()["access_token"]

        client2 = _get_client(user)
        response = client2.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["role"] == "investigator"
        assert data["employee_id"] == 100


class TestRefresh:
    @patch("app.api.auth.verify_password", return_value=True)
    def test_token_refresh(self, _mock_verify):
        user = _mock_user()
        client = _get_client(user)
        login_resp = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass"},
        )
        token = login_resp.json()["access_token"]

        client2 = _get_client(user)
        response = client2.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "investigator"
