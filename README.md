# Devin demo app

A tiny Flask task-tracker API, built only as a sandbox for a live Sable product demo of
Cognition's Devin. Not a real product.

## Run it

    pip install -r requirements.txt
    python app.py

## Run the tests

    pytest

`GET /tasks` accepts an optional `limit` query parameter (a non-negative integer); invalid
values return `400`. There's also a feature noted as a TODO: marking a task done and
deleting a task aren't implemented yet.
