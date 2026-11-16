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


def _create_tasks(client, done_flags):
    for i, done in enumerate(done_flags):
        client.post("/tasks", json={"title": f"Task {i}"})
        _tasks[-1]["done"] = done


def test_list_tasks_filters_by_status(client):
    _create_tasks(client, [False, True, False, True])

    open_tasks = client.get("/tasks?status=open").get_json()
    done_tasks = client.get("/tasks?status=done").get_json()

    assert [t["title"] for t in open_tasks] == ["Task 0", "Task 2"]
    assert [t["title"] for t in done_tasks] == ["Task 1", "Task 3"]


def test_list_tasks_without_status_returns_all(client):
    _create_tasks(client, [False, True])

    assert len(client.get("/tasks").get_json()) == 2


def test_list_tasks_rejects_unknown_status(client):
    r = client.get("/tasks?status=archived")
    assert r.status_code == 400
