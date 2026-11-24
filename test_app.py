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


def test_pages_do_not_repeat_tasks_across_boundaries(client):
    created_ids = [
        client.post("/tasks", json={"title": f"Task {i}"}).get_json()["id"]
        for i in range(7)
    ]

    page_size = 3
    seen_ids = []
    for offset in range(0, len(created_ids), page_size):
        r = client.get(f"/tasks?offset={offset}&limit={page_size}")
        assert r.status_code == 200
        page = r.get_json()
        assert len(page) <= page_size
        seen_ids.extend(t["id"] for t in page)

    assert len(seen_ids) == len(set(seen_ids)), f"tasks repeated across pages: {seen_ids}"
    assert seen_ids == created_ids


@pytest.mark.parametrize("query", ["limit=abc", "offset=abc", "limit=-1", "offset=-1"])
def test_list_tasks_rejects_invalid_pagination(client, query):
    r = client.get(f"/tasks?{query}")
    assert r.status_code == 400
