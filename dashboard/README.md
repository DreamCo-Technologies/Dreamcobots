# DreamCo Main Dashboard

Real-time revenue, lead count, and bot-scaling status for the DreamCo Money Operating System.

## Features

- Live revenue totals and per-bot breakdown
- Lead generation counts
- Conversion rate tracking
- Bot scaling status (auto-refreshes every 30 s)

## Endpoints

| Method | Route       | Description                           |
|--------|-------------|---------------------------------------|
| GET    | `/`         | HTML dashboard (auto-refresh 30 s)    |
| GET    | `/api/data` | Raw JSON cycle data                   |
| GET    | `/health`   | Liveness probe                        |

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (default port 5001)
python app.py

# Or specify a custom port
DASHBOARD_PORT=8080 python app.py
```

The dashboard will be available at <http://localhost:5001>.

## Deploying to Heroku / Railway

```bash
# Heroku
heroku create dreamco-main-dashboard
git push heroku main

# Railway
railway up
```

The `Procfile` already contains the correct start command:

```
web: python app.py
```

## Environment Variables

| Variable         | Default | Description           |
|------------------|---------|-----------------------|
| `DASHBOARD_PORT` | `5001`  | Port the server binds |
