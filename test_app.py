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


@pytest.mark.parametrize("limit", [0, 1, 3, 5])
def test_list_tasks_limit_returns_exactly_limit_items(client, limit):
    titles = [f"Task {i}" for i in range(5)]
    for t in titles:
        client.post("/tasks", json={"title": t})

    body = client.get(f"/tasks?limit={limit}").get_json()
    assert [t["title"] for t in body] == titles[:limit]


def test_list_tasks_limit_does_not_overlap_next_page(client):
    titles = [f"Task {i}" for i in range(4)]
    for t in titles:
        client.post("/tasks", json={"title": t})

    first_page = [t["title"] for t in client.get("/tasks?limit=2").get_json()]
    remaining = titles[len(first_page):]
    assert first_page == titles[:2]
    assert not set(first_page) & set(remaining)
