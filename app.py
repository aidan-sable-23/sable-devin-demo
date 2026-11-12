"""A tiny in-memory task tracker API, built for a live product demo."""
from flask import Flask, jsonify, request

app = Flask(__name__)
_tasks = []
_next_id = 1


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
    limit = int(request.args.get("limit", len(_tasks)))
    return jsonify(_tasks[:limit])


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
