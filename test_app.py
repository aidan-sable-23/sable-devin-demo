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


@pytest.mark.parametrize("limit, expected_titles", [
    (0, []),
    (1, ["Task 0"]),
    (3, ["Task 0", "Task 1", "Task 2"]),
    (10, ["Task 0", "Task 1", "Task 2"]),
])
def test_list_tasks_limit_boundaries(client, limit, expected_titles):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})

    r = client.get(f"/tasks?limit={limit}")
    assert r.status_code == 200
    assert [t["title"] for t in r.get_json()] == expected_titles


def test_list_tasks_without_limit_returns_all(client):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})

    r = client.get("/tasks")
    assert [t["title"] for t in r.get_json()] == ["Task 0", "Task 1", "Task 2"]
