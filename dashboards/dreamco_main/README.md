# DreamCo Main Dashboard

> **Source folder:** [`dashboard/`](../../dashboard/)

Real-time revenue, lead count, and bot-scaling status for the DreamCo Money Operating System. Powered by Flask.

## Quick Start

```bash
# From repo root
pip install -r dashboard/requirements.txt
python dashboard/app.py
# → http://localhost:5001
```

## Deploy

See [`dashboard/README.md`](../../dashboard/README.md) for full deployment instructions (Heroku, Railway, local).

## Endpoints

| Method | Route       | Description                      |
|--------|-------------|----------------------------------|
| GET    | `/`         | HTML dashboard (auto-refresh)    |
| GET    | `/api/data` | Raw JSON cycle data              |
| GET    | `/health`   | Liveness probe                   |
