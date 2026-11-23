# Devin demo app

A tiny Flask task-tracker API, built only as a sandbox for a live Sable product demo of
Cognition's Devin. Not a real product.

## Run it

    pip install -r requirements.txt
    python app.py

## Endpoints

| Method | Path | Notes |
| --- | --- | --- |
| `POST` | `/tasks` | Body `{"title": ..., "priority": "low"\|"medium"\|"high"}`; `priority` defaults to `medium`, other values return 400. |
| `GET` | `/tasks` | Optional `limit`. |
| `GET` | `/tasks/<id>` | 404 if missing. |
| `GET` | `/tasks/search?q=...` | Case-insensitive substring match on title; 400 if `q` is missing or blank. |
| `POST` | `/tasks/bulk-delete` | Body `{"ids": [1, 2]}`; returns `{"deleted": [...], "not_found": [...]}`, 400 unless `ids` is a list of integers. |
| `GET` | `/activity` | Log of task changes (`created`, `deleted`) with task id, title, and UTC timestamp. |

## Run the tests

    pytest

`test_list_tasks_respects_limit` currently fails — there is an off-by-one bug in the
`GET /tasks` pagination (see `app.py`). There's also a feature noted as a TODO: marking a
task done and deleting a task aren't implemented yet.
