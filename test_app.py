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
    ids = [client.post("/tasks", json={"title": f"Task {i}"}).get_json()["id"] for i in range(5)]

    page_size = 2
    first_page = client.get(f"/tasks?limit={page_size}").get_json()
    first_two_pages = client.get(f"/tasks?limit={2 * page_size}").get_json()
    second_page = first_two_pages[page_size:]

    first_ids = [t["id"] for t in first_page]
    second_ids = [t["id"] for t in second_page]
    assert not set(first_ids) & set(second_ids), f"task repeated across pages: {first_ids} / {second_ids}"
    assert first_ids + second_ids == ids[: 2 * page_size]
