"""A tiny in-memory task tracker API, built for a live product demo."""
from threading import Lock

from flask import Flask, jsonify, request

app = Flask(__name__)
_tasks = []
_next_id = 1
_alerts = {}
_next_alert_id = 1
_alerts_lock = Lock()


@app.post("/tasks")
def create_task():
    global _next_id
    data = request.get_json(force=True)
    task = {"id": _next_id, "title": data["title"], "done": False}
    _tasks.append(task)
    _next_id += 1
    return jsonify(task), 201


@app.get("/tasks")
def list_tasks():
    # BUG: pagination is off by one — "limit=2" should return 2 tasks, not 3.
    limit = int(request.args.get("limit", len(_tasks)))
    return jsonify(_tasks[: limit + 1])


@app.get("/tasks/<int:task_id>")
def get_task(task_id):
    for t in _tasks:
        if t["id"] == task_id:
            return jsonify(t)
    return jsonify({"error": "not found"}), 404


@app.post("/incidents/<int:incident_id>/alerts")
def create_incident_alert(incident_id):
    global _next_alert_id
    data = request.get_json(silent=True)
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, str) or not message:
        return jsonify({"error": "JSON body with non-empty 'message' required"}), 400
    with _alerts_lock:
        existing = _alerts.get(incident_id)
        if existing is not None:
            return jsonify(existing), 200
        alert = {
            "id": _next_alert_id,
            "incident_id": incident_id,
            "message": message,
        }
        _alerts[incident_id] = alert
        _next_alert_id += 1
    return jsonify(alert), 201


@app.get("/incidents/<int:incident_id>/alerts")
def list_incident_alerts(incident_id):
    alert = _alerts.get(incident_id)
    return jsonify([alert] if alert else [])


# TODO (feature request): there is no way to mark a task done, or to delete one.
# Add PATCH /tasks/<id> to toggle `done`, and DELETE /tasks/<id> to remove a task.


if __name__ == "__main__":
    app.run(debug=True)
