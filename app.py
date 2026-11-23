"""A tiny in-memory task tracker API, built for a live product demo."""
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)
_tasks = []
_next_id = 1
_activity = []

PRIORITIES = ("low", "medium", "high")
DEFAULT_PRIORITY = "medium"


def _log_activity(action, task):
    _activity.append(
        {
            "action": action,
            "task_id": task["id"],
            "title": task["title"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.post("/tasks")
def create_task():
    global _next_id
    data = request.get_json(force=True)
    if not isinstance(data.get("title"), str):
        return jsonify({"error": "title must be a string"}), 400
    priority = data.get("priority", DEFAULT_PRIORITY)
    if priority not in PRIORITIES:
        return jsonify({"error": f"priority must be one of {list(PRIORITIES)}"}), 400
    task = {"id": _next_id, "title": data["title"], "done": False, "priority": priority}
    _tasks.append(task)
    _next_id += 1
    _log_activity("created", task)
    return jsonify(task), 201


@app.post("/tasks/bulk-delete")
def bulk_delete_tasks():
    data = request.get_json(silent=True)
    ids = data.get("ids") if isinstance(data, dict) else None
    if not isinstance(ids, list) or not all(
        isinstance(i, int) and not isinstance(i, bool) for i in ids
    ):
        return jsonify({"error": "ids must be a list of integers"}), 400
    wanted = set(ids)
    deleted = [t for t in _tasks if t["id"] in wanted]
    _tasks[:] = [t for t in _tasks if t["id"] not in wanted]
    for t in deleted:
        _log_activity("deleted", t)
    deleted_ids = [t["id"] for t in deleted]
    not_found = sorted(wanted - set(deleted_ids))
    return jsonify({"deleted": deleted_ids, "not_found": not_found})


@app.get("/tasks/search")
def search_tasks():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "query parameter 'q' is required"}), 400
    needle = query.lower()
    return jsonify([t for t in _tasks if needle in t["title"].lower()])


@app.get("/activity")
def list_activity():
    return jsonify(_activity)


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


# TODO (feature request): there is no way to mark a task done, or to delete one.
# Add PATCH /tasks/<id> to toggle `done`, and DELETE /tasks/<id> to remove a task.


if __name__ == "__main__":
    app.run(debug=True)
