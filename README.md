# Devin demo app

A tiny Flask task-tracker API, built only as a sandbox for a live Sable product demo of
Cognition's Devin. Not a real product.

## Run it

    pip install -r requirements.txt
    python app.py

## Endpoints

- `POST /tasks` — create a task. Body: `title` (required), `status` (`todo` | `in_progress` | `done`,
  default `todo`), `tags` (list of strings), `due_date` (`YYYY-MM-DD`).
- `GET /tasks` — list tasks. Query params: `tag=<tag>` to filter, `sort=due_date` or
  `sort=-due_date` to sort (tasks without a due date go last), `limit=<n>`.
- `GET /tasks/<id>` — fetch one task.
- `GET /tasks/export` — download all tasks as CSV (tags joined with `;`).
- `GET /tasks/stats` — `{"total": n, "by_status": {"todo": n, "in_progress": n, "done": n}}`.

## Run the tests

    pytest

`test_list_tasks_respects_limit` currently fails — there is an off-by-one bug in the
`GET /tasks` pagination (see `app.py`). There's also a feature noted as a TODO: marking a
task done and deleting a task aren't implemented yet.
