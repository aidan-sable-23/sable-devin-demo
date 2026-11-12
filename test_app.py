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


def test_list_tasks_limit_edge_cases(client):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})

    assert len(client.get("/tasks").get_json()) == 3
    assert len(client.get("/tasks?limit=0").get_json()) == 0
    assert len(client.get("/tasks?limit=3").get_json()) == 3
    assert len(client.get("/tasks?limit=10").get_json()) == 3
    assert len(client.get("/tasks?limit=-1").get_json()) == 0
