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


def test_consecutive_pages_do_not_repeat_tasks(client):
    ids = [
        client.post("/tasks", json={"title": f"Task {i}"}).get_json()["id"]
        for i in range(5)
    ]

    page_size = 2
    pages = [
        [t["id"] for t in client.get(f"/tasks?limit={page_size}&offset={offset}").get_json()]
        for offset in range(0, len(ids), page_size)
    ]

    assert pages == [ids[0:2], ids[2:4], ids[4:5]]
    seen = [task_id for page in pages for task_id in page]
    assert len(seen) == len(set(seen)), f"tasks repeated across pages: {pages}"


@pytest.mark.parametrize("query", ["limit=abc", "offset=abc", "limit=-1", "offset=-1"])
def test_list_tasks_rejects_invalid_pagination(client, query):
    r = client.get(f"/tasks?{query}")
    assert r.status_code == 400
