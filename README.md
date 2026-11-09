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
