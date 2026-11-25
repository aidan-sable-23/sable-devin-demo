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


def test_list_tasks_pages_do_not_overlap(client):
    ids = [client.post("/tasks", json={"title": f"Task {i}"}).get_json()["id"] for i in range(6)]

    first_page = [t["id"] for t in client.get("/tasks?limit=3").get_json()]
    first_two_pages = [t["id"] for t in client.get("/tasks?limit=6").get_json()]
    second_page = first_two_pages[3:]

    assert first_page == ids[:3]
    assert second_page == ids[3:]
    assert not set(first_page) & set(second_page)
