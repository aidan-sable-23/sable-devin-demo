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


def test_completed_count_is_zero_for_empty_list(client):
    r = client.get("/tasks")
    assert r.get_json() == []
    assert r.headers["X-Completed-Count"] == "0"


def test_completed_count_counts_done_tasks(client):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})
    _tasks[0]["done"] = True
    _tasks[2]["done"] = True

    r = client.get("/tasks?limit=0")
    assert r.headers["X-Completed-Count"] == "2"
