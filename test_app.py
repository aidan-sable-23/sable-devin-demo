"""Run with: pytest test_app.py"""
import pytest
import app as app_module
from app import app, _tasks


@pytest.fixture(autouse=True)
def reset_state():
    _tasks.clear()
    app_module._next_id = 1
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


def test_list_tasks_limit_returns_first_n_in_order(client):
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"})

    body = client.get("/tasks?limit=3").get_json()
    assert [t["title"] for t in body] == ["Task 0", "Task 1", "Task 2"]


def test_list_tasks_limit_zero_returns_empty(client):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})

    assert client.get("/tasks?limit=0").get_json() == []


def test_list_tasks_limit_larger_than_total_returns_all(client):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})

    assert len(client.get("/tasks?limit=10").get_json()) == 3


def test_list_tasks_without_limit_returns_all(client):
    for i in range(4):
        client.post("/tasks", json={"title": f"Task {i}"})

    assert len(client.get("/tasks").get_json()) == 4
