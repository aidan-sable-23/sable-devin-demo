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


@pytest.mark.parametrize("limit, expected", [(0, 0), (1, 1), (4, 4), (5, 5), (6, 5), (100, 5)])
def test_list_tasks_limit_boundaries(client, limit, expected):
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"})

    r = client.get(f"/tasks?limit={limit}")
    assert r.status_code == 200
    assert [t["title"] for t in r.get_json()] == [f"Task {i}" for i in range(expected)]


def test_list_tasks_without_limit_returns_all(client):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})

    r = client.get("/tasks")
    assert r.status_code == 200
    assert len(r.get_json()) == 3


def test_list_tasks_limit_on_empty_list(client):
    r = client.get("/tasks?limit=3")
    assert r.status_code == 200
    assert r.get_json() == []


@pytest.mark.parametrize("limit", ["-1", "abc", "2.5", "", " 2", "²"])
def test_list_tasks_rejects_invalid_limit(client, limit):
    client.post("/tasks", json={"title": "Task"})

    r = client.get("/tasks", query_string={"limit": limit})
    assert r.status_code == 400
    assert "error" in r.get_json()
