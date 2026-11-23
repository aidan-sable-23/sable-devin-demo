"""Run with: pytest test_app.py"""
import pytest
from app import app, _tasks, _activity


@pytest.fixture(autouse=True)
def reset_state():
    _tasks.clear()
    _activity.clear()
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


def test_create_task_defaults_priority_to_medium(client):
    r = client.post("/tasks", json={"title": "No priority"})
    assert r.status_code == 201
    assert r.get_json()["priority"] == "medium"


@pytest.mark.parametrize("priority", ["low", "medium", "high"])
def test_create_task_accepts_valid_priority(client, priority):
    r = client.post("/tasks", json={"title": "Prioritized", "priority": priority})
    assert r.status_code == 201
    assert r.get_json()["priority"] == priority


@pytest.mark.parametrize("priority", ["urgent", "", None, 1, "HIGH"])
def test_create_task_rejects_invalid_priority(client, priority):
    r = client.post("/tasks", json={"title": "Bad", "priority": priority})
    assert r.status_code == 400
    assert _tasks == []


def test_search_matches_title_case_insensitively(client):
    a = client.post("/tasks", json={"title": "Write demo script"}).get_json()
    client.post("/tasks", json={"title": "Book flights"})
    b = client.post("/tasks", json={"title": "Record DEMO video"}).get_json()

    r = client.get("/tasks/search?q=demo")
    assert r.status_code == 200
    assert [t["id"] for t in r.get_json()] == [a["id"], b["id"]]


def test_search_with_no_matches_returns_empty_list(client):
    client.post("/tasks", json={"title": "Write demo script"})
    r = client.get("/tasks/search?q=nothing")
    assert r.status_code == 200
    assert r.get_json() == []


@pytest.mark.parametrize("qs", ["", "?q=", "?q=%20%20"])
def test_search_requires_query(client, qs):
    r = client.get(f"/tasks/search{qs}")
    assert r.status_code == 400


def test_bulk_delete_removes_listed_tasks(client):
    ids = [client.post("/tasks", json={"title": f"T{i}"}).get_json()["id"] for i in range(3)]
    missing = max(ids) + 100

    r = client.post("/tasks/bulk-delete", json={"ids": [ids[0], ids[2], missing]})
    assert r.status_code == 200
    assert r.get_json() == {"deleted": [ids[0], ids[2]], "not_found": [missing]}
    assert [t["id"] for t in _tasks] == [ids[1]]
    assert client.get(f"/tasks/{ids[0]}").status_code == 404


@pytest.mark.parametrize(
    "body", [None, {}, {"ids": "1"}, {"ids": [1, "2"]}, {"ids": [True]}, {"ids": 1}]
)
def test_bulk_delete_rejects_invalid_ids(client, body):
    client.post("/tasks", json={"title": "Keep me"})
    r = client.post("/tasks/bulk-delete", json=body)
    assert r.status_code == 400
    assert len(_tasks) == 1


def test_activity_log_records_create_and_delete(client):
    task = client.post("/tasks", json={"title": "Logged", "priority": "high"}).get_json()
    client.post("/tasks/bulk-delete", json={"ids": [task["id"]]})

    log = client.get("/activity").get_json()
    assert [(e["action"], e["task_id"]) for e in log] == [
        ("created", task["id"]),
        ("deleted", task["id"]),
    ]
    assert log[0]["task"] == task
    assert all(e["timestamp"] for e in log)


def test_activity_log_ignores_failed_operations(client):
    client.post("/tasks", json={"title": "Bad", "priority": "urgent"})
    client.post("/tasks/bulk-delete", json={"ids": [12345]})
    assert client.get("/activity").get_json() == []
