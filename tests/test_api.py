"""Tests call the real application through FastAPI's TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    # A fresh app per test, so no test depends on another's notes.
    return TestClient(create_app())


def test_root_answers(client):
    r = client.get("/")
    assert r.status_code == 201
    assert r.json()["service"] == "notes"


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_notes_start_empty(client):
    r = client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []


def test_create_and_get_note(client):
    r = client.post("/notes", json={"text": "buy milk"})
    assert r.status_code == 201
    note = r.json()
    assert note["text"] == "buy milk"

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json() == note


def test_create_requires_text(client):
    r = client.post("/notes", json={"text": "   "})
    assert r.status_code == 422


def test_delete_note(client):
    note = client.post("/notes", json={"text": "temporary"}).json()
    assert client.delete(f"/notes/{note['id']}").status_code == 204
    assert client.get(f"/notes/{note['id']}").status_code == 404


def test_unknown_note_is_404(client):
    assert client.get("/notes/999").status_code == 404
