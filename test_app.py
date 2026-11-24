"""Run with: pytest test_app.py"""
import pytest
from app import app, _tasks, paginate


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


def test_list_tasks_without_limit_returns_all(client):
    for i in range(3):
        client.post("/tasks", json={"title": f"Task {i}"})

    r = client.get("/tasks")
    assert [t["title"] for t in r.get_json()] == ["Task 0", "Task 1", "Task 2"]


@pytest.mark.parametrize(
    "items, limit, expected",
    [
        ([], 0, []),
        ([1, 2, 3], 3, [1, 2, 3]),
        ([1, 2, 3], 10, [1, 2, 3]),
        # Current off-by-one behavior, preserved by the refactor.
        ([1, 2, 3, 4, 5], 2, [1, 2, 3]),
        ([1, 2, 3], 0, [1]),
    ],
)
def test_paginate(items, limit, expected):
    assert paginate(items, limit) == expected
