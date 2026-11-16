# Devin demo app

A tiny Flask task-tracker API, built only as a sandbox for a live Sable product demo of
Cognition's Devin. Not a real product.

## Run it

    pip install -r requirements.txt
    python app.py

## Filter tasks by status

`GET /tasks?status=open` returns tasks that aren't done; `GET /tasks?status=done` returns
completed ones. Any other `status` value returns `400`. Omit `status` to get every task.

## Run the tests

    pytest

`test_list_tasks_respects_limit` currently fails — there is an off-by-one bug in the
`GET /tasks` pagination (see `app.py`). There's also a feature noted as a TODO: marking a
task done and deleting a task aren't implemented yet.
