# Notes service

INF 345 semester project. A small HTTP API for keeping short text notes.

## What it does

A notes API written in Python with FastAPI and served by uvicorn. Notes are
kept in memory, so they disappear when the service stops. Interactive API docs
are at `/docs`.

| Method   | Path          | What it does                              |
|----------|---------------|-------------------------------------------|
| `GET`    | `/`           | Service name and link to the docs         |
| `GET`    | `/healthz`    | Health check: `200 {"status": "ok"}`      |
| `GET`    | `/notes`      | All notes                                 |
| `POST`   | `/notes`      | Create a note, body `{"text": "..."}`     |
| `GET`    | `/notes/<id>` | One note, or `404`                        |
| `DELETE` | `/notes/<id>` | Delete a note (`204`), or `404`           |

An empty `text` is rejected with `422`.

## How to run it

Requires Python 3.9 or newer. The first run creates `.venv/` and installs the
dependencies from `requirements.txt` and `requirements-dev.txt`; later runs reuse it.

```bash
./scripts/run.sh                 # listens on port 8080
PORT=9000 ./scripts/run.sh       # listens on port 9000
```

### Port

The service listens on the port given in the `PORT` environment variable and
defaults to `8080` when it is not set. The port is never hardcoded, so Docker,
Kubernetes or any platform can choose it.

Try it:

```bash
curl localhost:8080/healthz
curl -X POST localhost:8080/notes -H 'Content-Type: application/json' -d '{"text": "buy milk"}'
curl localhost:8080/notes
```

## How to test it

```bash
./scripts/test.sh
```

The tests in `tests/` use pytest and FastAPI's `TestClient` to call the real
application. The script exits `0` only when every test passes and always ends with
one line in the form `TESTS: <passed>/<total>`.

## Layout

```
app/main.py          the FastAPI application
tests/test_api.py    tests against the application
scripts/run.sh       starts the service with uvicorn
scripts/test.sh      runs the tests
scripts/_venv.sh     creates .venv and installs dependencies
```
