# Streak.txt local API

The FastAPI application exposes the shared `streak_core` service as a REST API
and an HTMX interface. See the repository [`README.md`](../README.md) for the
authoritative installation, launch, testing, and packaging workflows.

Run it from the repository root:

```bash
.env/bin/python run_api.py
```

The application binds to `127.0.0.1:8000` and uses `~/streaks` unless
`STREAKS_DIR` is deliberately set. Interactive API documentation is available
at `http://127.0.0.1:8000/docs`.

## Routes

- `GET /api/v1/streaks`
- `GET /api/v1/streaks/{id}`
- `POST /api/v1/streaks`
- `PUT /api/v1/streaks/{id}`
- `DELETE /api/v1/streaks/{id}` (moves the file to `archive/`)
- `POST /api/v1/streaks/{id}/tick`
- `POST /api/v1/streaks/{id}/ticks`

New streaks are stored as `streak-{id}.txt`. For example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/streaks \
  -H 'Content-Type: application/json' \
  -d '{"name":"Morning walk","tick_type":"Daily"}'

curl -X POST http://127.0.0.1:8000/api/v1/streaks/morning-walk/tick
```

The browser UI uses a bundled HTMX asset and does not require internet access.
Write requests carrying a foreign browser `Origin` are rejected.
