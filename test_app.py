"""Run with: pytest test_app.py"""
from concurrent.futures import ThreadPoolExecutor

import pytest
from app import app, _tasks, _alerts


@pytest.fixture(autouse=True)
def reset_state():
    _tasks.clear()
    _alerts.clear()
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


def test_duplicate_incident_alert_is_not_created(client):
    first = client.post("/incidents/42/alerts", json={"message": "CPU high"})
    second = client.post("/incidents/42/alerts", json={"message": "CPU high"})

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.get_json() == first.get_json()
    assert client.get("/incidents/42/alerts").get_json() == [first.get_json()]


def test_concurrent_alerts_for_same_incident_create_one_alert():
    def post(_):
        return app.test_client().post("/incidents/9/alerts", json={"message": "down"})

    with ThreadPoolExecutor(max_workers=8) as pool:
        responses = list(pool.map(post, range(32)))

    assert sorted(r.status_code for r in responses).count(201) == 1
    assert len({r.get_json()["id"] for r in responses}) == 1
    assert len(app.test_client().get("/incidents/9/alerts").get_json()) == 1


def test_alerts_for_different_incidents_are_separate(client):
    a = client.post("/incidents/1/alerts", json={"message": "disk full"})
    b = client.post("/incidents/2/alerts", json={"message": "disk full"})

    assert a.status_code == 201
    assert b.status_code == 201
    assert a.get_json()["id"] != b.get_json()["id"]


@pytest.mark.parametrize(
    "kwargs",
    [{"data": "not json"}, {"json": ["a"]}, {"json": {}}, {"json": {"message": "  "}}],
)
def test_invalid_alert_request_is_rejected_without_creating_alert(client, kwargs):
    r = client.post("/incidents/7/alerts", **kwargs)
    assert r.status_code == 400
    assert client.get("/incidents/7/alerts").get_json() == []

    retry = client.post("/incidents/7/alerts", json={"message": "real message"})
    assert retry.status_code == 201
    assert retry.get_json()["message"] == "real message"
