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


def test_list_tasks_page_does_not_include_next_pages_first_item(client):
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"})

    page = client.get("/tasks?limit=2").get_json()
    titles = [t["title"] for t in page]
    assert titles == ["Task 0", "Task 1"]
    assert "Task 2" not in titles, "first item of the next page leaked into this page"


@pytest.mark.parametrize("limit", [1, 4, 5, 10])
def test_list_tasks_limit_boundaries(client, limit):
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"})

    body = client.get(f"/tasks?limit={limit}").get_json()
    assert len(body) == min(limit, 5)
