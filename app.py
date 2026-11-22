"""A tiny in-memory task tracker API, built for a live product demo."""
import csv
import io
from datetime import date

from flask import Flask, Response, jsonify, request

app = Flask(__name__)
_tasks = []
_next_id = 1

STATUSES = ("todo", "in_progress", "done")
CSV_FIELDS = ("id", "title", "status", "done", "tags", "due_date")


def _csv_safe(value):
    # Neutralize spreadsheet formula injection (OWASP CSV injection guidance).
    if value and value[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


def _parse_due_date(value):
    if value is None:
        return None
    return date.fromisoformat(value).isoformat()


@app.post("/tasks")
def create_task():
    global _next_id
    data = request.get_json(force=True)
    status = data.get("status", "todo")
    if status not in STATUSES:
        return jsonify({"error": f"status must be one of {list(STATUSES)}"}), 400
    tags = data.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        return jsonify({"error": "tags must be a list of strings"}), 400
    try:
        due_date = _parse_due_date(data.get("due_date"))
    except (TypeError, ValueError):
        return jsonify({"error": "due_date must be an ISO date (YYYY-MM-DD)"}), 400
    task = {
        "id": _next_id,
        "title": data["title"],
        "status": status,
        "done": status == "done",
        "tags": tags,
        "due_date": due_date,
    }
    _tasks.append(task)
    _next_id += 1
    return jsonify(task), 201


@app.get("/tasks")
def list_tasks():
    # BUG: pagination is off by one — "limit=2" should return 2 tasks, not 3.
    tasks = _tasks
    tag = request.args.get("tag")
    if tag is not None:
        tasks = [t for t in tasks if tag in t["tags"]]

    sort = request.args.get("sort")
    if sort is not None:
        if sort not in ("due_date", "-due_date"):
            return jsonify({"error": "sort must be 'due_date' or '-due_date'"}), 400
        dated = [t for t in tasks if t["due_date"] is not None]
        undated = [t for t in tasks if t["due_date"] is None]
        dated.sort(key=lambda t: t["due_date"], reverse=sort.startswith("-"))
        tasks = dated + undated

    limit = int(request.args.get("limit", len(tasks)))
    return jsonify(tasks[: limit + 1])


@app.get("/tasks/export")
def export_tasks():
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for t in _tasks:
        writer.writerow({
            **t,
            "title": _csv_safe(t["title"]),
            "tags": _csv_safe(";".join(t["tags"])),
            "due_date": t["due_date"] or "",
        })
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks.csv"},
    )


@app.get("/tasks/stats")
def task_stats():
    by_status = {s: 0 for s in STATUSES}
    for t in _tasks:
        by_status[t["status"]] += 1
    return jsonify({"total": len(_tasks), "by_status": by_status})


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
