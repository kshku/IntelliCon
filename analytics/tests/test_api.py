from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "intellicon-analytics"


def test_list_jobs():
    response = client.get("/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)
    assert len(jobs) >= 3
    names = [j["name"] for j in jobs]
    assert "hotspot_detection" in names
    assert "trend_analysis" in names
    assert "predictive_analytics" in names


def test_get_job():
    response = client.get("/jobs/hotspot_detection")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "hotspot_detection"
    assert data["schedule"] == "cron"
    assert data["schedule_kwargs"]["hour"] == 2


def test_get_job_not_found():
    response = client.get("/jobs/nonexistent")
    assert response.status_code == 404


def test_list_executions():
    response = client.get("/executions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_execution_not_found():
    response = client.get("/executions/999999")
    assert response.status_code == 404
