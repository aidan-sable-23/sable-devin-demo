"""Run with: pytest test_app.py"""
import pytest
from app import app, _tasks, _alerts


@pytest.fixture(autouse=True)
def reset_state():
    _tasks.clear()
    _alerts.clear()
    yield


@pytest.fixture
def client():
    return app.test_client()


def test_create_task(client):
    r = client.post("/tasks", json={"title": "Write demo script"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Write demo script"


def test_list_tasks_respects_limit(client):
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"})

    r = client.get("/tasks?limit=2")
    body = r.get_json()
    assert len(body) == 2, f"expected 2 tasks with limit=2, got {len(body)}"


def test_duplicate_incident_alert_is_not_created(client):
    first = client.post("/incidents/42/alerts", json={"message": "CPU high"})
    second = client.post("/incidents/42/alerts", json={"message": "CPU high"})

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.get_json()["id"] == first.get_json()["id"]
    assert len(client.get("/incidents/42/alerts").get_json()) == 1


def test_alerts_for_different_incidents_are_separate(client):
    a = client.post("/incidents/1/alerts", json={"message": "disk full"})
    b = client.post("/incidents/2/alerts", json={"message": "disk full"})

    assert a.status_code == 201
    assert b.status_code == 201
    assert a.get_json()["id"] != b.get_json()["id"]
