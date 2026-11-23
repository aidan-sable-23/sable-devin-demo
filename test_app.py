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
    assert r.get_json()["priority"] == "medium"


def test_create_task_with_valid_priority(client):
    r = client.post("/tasks", json={"title": "Urgent", "priority": "high"})
    assert r.status_code == 201
    assert r.get_json()["priority"] == "high"


@pytest.mark.parametrize("priority", ["urgent", "", None, 3, "HIGH"])
def test_create_task_rejects_invalid_priority(client, priority):
    r = client.post("/tasks", json={"title": "Bad", "priority": priority})
    assert r.status_code == 400
    assert _tasks == []


def test_bulk_delete_removes_listed_tasks(client):
    ids = [client.post("/tasks", json={"title": f"T{i}"}).get_json()["id"] for i in range(3)]
    r = client.post("/tasks/bulk-delete", json={"ids": [ids[0], ids[2], 999999]})
    assert r.status_code == 200
    assert r.get_json() == {"deleted": [ids[0], ids[2]], "not_found": [999999]}
    assert [t["id"] for t in _tasks] == [ids[1]]


@pytest.mark.parametrize("body", [{}, {"ids": "1"}, {"ids": [1, "2"]}, {"ids": [True]}])
def test_bulk_delete_rejects_invalid_ids(client, body):
    client.post("/tasks", json={"title": "Keep me"})
    r = client.post("/tasks/bulk-delete", json=body)
    assert r.status_code == 400
    assert len(_tasks) == 1


def test_search_matches_title_case_insensitively(client):
    for title in ["Write demo script", "Review DEMO notes", "Buy milk"]:
        client.post("/tasks", json={"title": title})
    r = client.get("/tasks/search?q=demo")
    assert r.status_code == 200
    assert [t["title"] for t in r.get_json()] == ["Write demo script", "Review DEMO notes"]


def test_search_requires_query(client):
    assert client.get("/tasks/search").status_code == 400
    assert client.get("/tasks/search?q=%20").status_code == 400


def test_activity_log_records_create_and_delete(client):
    task_id = client.post("/tasks", json={"title": "Logged"}).get_json()["id"]
    client.post("/tasks/bulk-delete", json={"ids": [task_id]})
    log = client.get("/activity").get_json()
    assert [(e["action"], e["task_id"], e["title"]) for e in log] == [
        ("created", task_id, "Logged"),
        ("deleted", task_id, "Logged"),
    ]
    assert all(e["timestamp"] for e in log)


def test_activity_log_skips_rejected_changes(client):
    client.post("/tasks", json={"title": "Bad", "priority": "urgent"})
    client.post("/tasks/bulk-delete", json={"ids": [12345]})
    assert client.get("/activity").get_json() == []


@pytest.mark.parametrize("body", [{}, {"title": None}, {"title": 5}])
def test_create_task_rejects_non_string_title(client, body):
    r = client.post("/tasks", json=body)
    assert r.status_code == 400
    assert _tasks == []
    assert client.get("/tasks/search?q=x").status_code == 200
