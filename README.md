# Devin demo app

A tiny Flask task-tracker API, built only as a sandbox for a live Sable product demo of
Cognition's Devin. Not a real product.

## Run it

    pip install -r requirements.txt
    python app.py

## Run the tests

    pytest

`test_list_tasks_respects_limit` currently fails — there is an off-by-one bug in the
`GET /tasks` pagination (see `app.py`). There's also a feature noted as a TODO: marking a
task done and deleting a task aren't implemented yet.

## Endpoints

| Method | Path | Notes |
| --- | --- | --- |
| `POST` | `/tasks` | Body `{"title": ..., "priority": "low" \| "medium" \| "high"}`; priority defaults to `medium`, anything else returns 400. |
| `GET` | `/tasks` | Optional `limit`. |
| `GET` | `/tasks/<id>` | 404 if missing. |
| `GET` | `/tasks/search?q=...` | Case-insensitive substring match on title; 400 if `q` is empty. |
| `POST` | `/tasks/bulk-delete` | Body `{"ids": [1, 2]}`; returns `{"deleted": [...], "not_found": [...]}`. |
| `GET` | `/activity` | Log of task changes (`created`, `deleted`) with a task snapshot and UTC timestamp. |
