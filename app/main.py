"""A small notes API. Notes are kept in memory."""

import threading

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, field_validator


class NoteIn(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def not_blank(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("text must not be empty")
        return value


class Note(BaseModel):
    id: int
    text: str


class NoteStore:
    def __init__(self):
        self._notes = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def list(self):
        with self._lock:
            return list(self._notes.values())

    def get(self, note_id):
        with self._lock:
            return self._notes.get(note_id)

    def add(self, text):
        with self._lock:
            note = Note(id=self._next_id, text=text)
            self._notes[note.id] = note
            self._next_id += 1
            return note

    def delete(self, note_id):
        with self._lock:
            return self._notes.pop(note_id, None) is not None


def create_app():
    app = FastAPI(title="Notes service")
    store = NoteStore()

    @app.get("/")
    def root():
        return {"service": "notes", "docs": "/docs"}

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/notes", response_model=list[Note])
    def list_notes():
        return store.list()

    @app.post("/notes", response_model=Note, status_code=201)
    def create_note(note: NoteIn):
        return store.add(note.text)

    @app.get("/notes/{note_id}", response_model=Note)
    def get_note(note_id: int):
        note = store.get(note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="note not found")
        return note

    @app.delete("/notes/{note_id}", status_code=204)
    def delete_note(note_id: int):
        if not store.delete(note_id):
            raise HTTPException(status_code=404, detail="note not found")
        return Response(status_code=204)

    return app


app = create_app()
