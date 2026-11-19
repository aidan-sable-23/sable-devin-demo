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


def test_list_tasks_returns_consecutive_pages_without_duplicates(client):
    task_ids = [
        client.post("/tasks", json={"title": f"Task {i}"}).get_json()["id"]
        for i in range(5)
    ]

    page_ids = []
    for offset in (0, 2, 4):
        response = client.get("/tasks", query_string={"limit": 2, "offset": offset})
        assert response.status_code == 200
        page_ids.append([task["id"] for task in response.get_json()])

    assert page_ids == [task_ids[:2], task_ids[2:4], task_ids[4:]]
