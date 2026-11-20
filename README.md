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
curl localhost:8080/notes/1
curl -X DELETE localhost:8080/notes/1
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

## GitOps deployment (M5)

Argo CD watches `main` in this repository and deploys the manifests from `k8s/`
into the `default` namespace. Its Application is `notes` in namespace `argocd`.
CI tests, builds, scans and publishes images; Argo CD deploys them. Images in
`k8s/deployment.yaml` are pinned to full commit SHAs from successful CI runs.

Create `app-secret` with the `API_KEY` key separately in the cluster; never put
its value or a Secret manifest in Git. With Argo CD installed, register the app:

```bash
kubectl apply -f argocd/application.yaml
kubectl -n argocd get application notes
```

`selfHeal: true` restores manual changes (including replica count and a deleted
Service). `prune: true` removes managed resources removed from Git. The desired
replica count is 2. To release an image, change its SHA in `k8s/deployment.yaml`,
open a pull request, and merge it into `main`.

The `M5 check` pull-request workflow runs the official static and live marker
in a disposable kind cluster, including sync, self-heal and pruning checks.

## Rollback

Argo CD deploys what is on the `main` branch, from the `k8s` folder.
To roll back, undo the commit that deployed the bad version with a new commit:

```bash
git switch main
git pull --ff-only
git log --oneline -- k8s/deployment.yaml
git revert <image-bump-commit-sha>
git push origin main
```

Replace `<image-bump-commit-sha>` with the commit that changed the image. For a
merge commit, use `git revert -m 1 <merge-commit-sha>` instead; for a squash merge,
use ordinary `git revert`. If main requires pull requests, push the revert on a
new branch and merge its pull request.

Argo CD deploys the previous version within three minutes. To request a refresh
and inspect the result:

```bash
kubectl -n argocd annotate application notes argocd.argoproj.io/refresh=normal --overwrite
kubectl -n argocd get application notes
kubectl get deployment notes -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Wait for the Application to report `Synced` and `Healthy`, and check the image
SHA is the previous version. Do not use `kubectl rollout undo`: self-heal would
put the bad version back because Git still declares it.
