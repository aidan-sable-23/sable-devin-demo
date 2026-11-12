"""Run with: pytest test_app.py"""
import pytest
from app import app, _tasks


@pytest.fixture(autouse=True)
def reset_state():
    _tasks.clear()
    yield


@pytest.fixture
def client():
    return app.test_client()


def create_task(client, title):
    return client.post("/tasks", json={"title": title})


def test_create_task(client):
    r = create_task(client, "Write demo script")
    assert r.status_code == 201
    assert r.get_json()["title"] == "Write demo script"


def test_list_tasks_respects_limit(client):
    for i in range(5):
        create_task(client, f"Task {i}")

    r = client.get("/tasks?limit=2")
    body = r.get_json()
    assert len(body) == 2, f"expected 2 tasks with limit=2, got {len(body)}"


def test_get_task_returns_created_task(client):
    created = create_task(client, "Rehearse demo").get_json()

    r = client.get(f"/tasks/{created['id']}")
    assert r.status_code == 200
    assert r.get_json() == created


def test_get_task_missing_returns_404(client):
    r = client.get("/tasks/999999")
    assert r.status_code == 404
    assert r.get_json() == {"error": "not found"}
