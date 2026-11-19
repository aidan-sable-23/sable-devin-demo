# Devin demo app

A tiny Flask task-tracker API, built only as a sandbox for a live Sable product demo of
Cognition's Devin. Not a real product.

## Run it

    pip install -r requirements.txt
    python app.py

## List tasks

`GET /tasks` returns all tasks by default. Use `limit` for the maximum page
size and `offset` for the number of tasks to skip. For example, request
`/tasks?limit=2` and then `/tasks?limit=2&offset=2` for the first two pages.

## Run the tests

    pytest

Marking a task done and deleting a task are still TODOs.
