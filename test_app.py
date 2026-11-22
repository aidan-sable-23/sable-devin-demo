"""Run with: pytest test_app.py"""
import csv
import io

from datetime import date

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


def _titles(resp):
    return [t["title"] for t in resp.get_json()]


def test_create_task_defaults(client):
    body = client.post("/tasks", json={"title": "A"}).get_json()
    assert body["status"] == "todo"
    assert body["done"] is False
    assert body["tags"] == []
    assert body["due_date"] is None


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": 123},
        {"title": None},
        {"title": "A", "status": "blocked"},
        {"title": "A", "tags": "urgent"},
        {"title": "A", "due_date": "next tuesday"},
    ],
)
def test_create_task_rejects_invalid_fields(client, payload):
    assert client.post("/tasks", json=payload).status_code == 400


def test_export_tasks_csv(client):
    a = client.post(
        "/tasks", json={"title": "A", "status": "done", "tags": ["x", "y"], "due_date": "2026-12-01"}
    ).get_json()
    b = client.post("/tasks", json={"title": "B, with comma"}).get_json()

    r = client.get("/tasks/export")
    assert r.status_code == 200
    assert r.mimetype == "text/csv"
    assert r.headers["Content-Disposition"] == f"attachment; filename=tasks-{date.today().isoformat()}.csv"
    rows = list(csv.DictReader(io.StringIO(r.get_data(as_text=True))))
    assert rows == [
        {"id": str(a["id"]), "title": "A", "status": "done", "done": "True", "tags": "x;y", "due_date": "2026-12-01"},
        {"id": str(b["id"]), "title": "B, with comma", "status": "todo", "done": "False", "tags": "", "due_date": ""},
    ]


def test_export_tasks_csv_columns_match_task_fields(client):
    client.post("/tasks", json={"title": "A"})
    header = client.get("/tasks/export").get_data(as_text=True).splitlines()[0]
    assert header.split(",") == list(_tasks[0].keys())


def test_export_tasks_csv_empty(client):
    r = client.get("/tasks/export")
    assert r.get_data(as_text=True).strip() == "id,title,status,done,tags,due_date"


def test_export_tasks_csv_neutralizes_formulas(client):
    client.post("/tasks", json={"title": "=HYPERLINK(\"http://evil\")", "tags": ["+cmd", "ok"]})
    client.post("/tasks", json={"title": "-1+1"})
    client.post("/tasks", json={"title": "@SUM(A1)"})
    rows = list(csv.DictReader(io.StringIO(client.get("/tasks/export").get_data(as_text=True))))
    assert [r["title"] for r in rows] == ["'=HYPERLINK(\"http://evil\")", "'-1+1", "'@SUM(A1)"]
    assert rows[0]["tags"] == "'+cmd;ok"


def test_task_stats(client):
    for status in ("todo", "todo", "in_progress", "done"):
        client.post("/tasks", json={"title": status, "status": status})
    assert client.get("/tasks/stats").get_json() == {
        "total": 4,
        "by_status": {"todo": 2, "in_progress": 1, "done": 1},
    }


def test_task_stats_empty(client):
    assert client.get("/tasks/stats").get_json() == {
        "total": 0,
        "by_status": {"todo": 0, "in_progress": 0, "done": 0},
    }


def test_filter_tasks_by_tag(client):
    client.post("/tasks", json={"title": "A", "tags": ["work"]})
    client.post("/tasks", json={"title": "B", "tags": ["home"]})
    client.post("/tasks", json={"title": "C", "tags": ["work", "urgent"]})
    assert _titles(client.get("/tasks?tag=work")) == ["A", "C"]
    assert _titles(client.get("/tasks?tag=none")) == []


def test_filter_tasks_by_tag_is_case_insensitive(client):
    client.post("/tasks", json={"title": "A", "tags": ["Work"]})
    client.post("/tasks", json={"title": "B", "tags": ["home"]})
    client.post("/tasks", json={"title": "C", "tags": ["WORK"]})
    assert _titles(client.get("/tasks?tag=work")) == ["A", "C"]
    assert _titles(client.get("/tasks?tag=wOrK")) == ["A", "C"]
    assert client.get("/tasks?tag=work").get_json()[0]["tags"] == ["Work"]


def test_sort_tasks_by_due_date(client):
    client.post("/tasks", json={"title": "late", "due_date": "2026-12-31"})
    client.post("/tasks", json={"title": "undated"})
    client.post("/tasks", json={"title": "early", "due_date": "2026-01-15"})
    assert _titles(client.get("/tasks?sort=due_date")) == ["early", "late", "undated"]
    assert _titles(client.get("/tasks?sort=-due_date")) == ["late", "early", "undated"]


def test_sort_tasks_rejects_unknown_field(client):
    assert client.get("/tasks?sort=title").status_code == 400


def test_filter_and_sort_combined(client):
    client.post("/tasks", json={"title": "A", "tags": ["work"], "due_date": "2026-05-01"})
    client.post("/tasks", json={"title": "B", "tags": ["home"], "due_date": "2026-01-01"})
    client.post("/tasks", json={"title": "C", "tags": ["work"], "due_date": "2026-02-01"})
    assert _titles(client.get("/tasks?tag=work&sort=due_date")) == ["C", "A"]
