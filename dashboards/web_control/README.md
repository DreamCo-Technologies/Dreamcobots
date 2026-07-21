# Web Control Dashboard

Flask-based centralized control interface for the DreamCo bot ecosystem.

## Features

- Real-time bot activity, performance logs, and revenue monitoring
- Manual bot creation, management, and overrides
- Go Live buttons for high-revenue bots
- Bot leaderboard and underperformer detection
- Full REST API for browser-based visualization

## Endpoints

| Method | Route                        | Description                                  |
|--------|------------------------------|----------------------------------------------|
| GET    | `/`                          | Dashboard HTML landing page                  |
| GET    | `/api/status`                | System-wide status JSON                      |
| GET    | `/api/bots`                  | Registered bot list with KPI scores          |
| POST   | `/api/bots/register`         | Register a new bot                           |
| POST   | `/api/bots/<name>/go_live`   | Deploy / activate a bot instance             |
| GET    | `/api/bots/catalog`          | Full bot catalog with Go Live status         |
| GET    | `/api/revenue`               | Revenue summary JSON                         |
| GET    | `/api/leaderboard`           | Bot leaderboard (top by composite KPI)       |
| GET    | `/api/underperformers`       | Bots with composite score below threshold    |
| POST   | `/api/record_run`            | Record a bot run with KPIs                   |
| GET    | `/api/history/<bot_name>`    | Run history for a specific bot               |

## Source

Implementation: [`ui/web_dashboard.py`](../../ui/web_dashboard.py)

## Running Locally

```bash
# From the repo root — install dependencies
pip install -r dashboards/web_control/requirements.txt

# Start the server (default port 5050)
python dashboards/web_control/run.py

# Or specify a custom port
PORT=8080 python dashboards/web_control/run.py
```

The dashboard will be available at <http://localhost:5050>.

## Deploying to Heroku / Railway

```bash
# Copy this folder to its own repo or deploy from the monorepo root
heroku create dreamco-web-control
git push heroku main
```

The `Procfile` contains the correct start command:

```
web: python run.py
```

## Environment Variables

| Variable | Default | Description           |
|----------|---------|-----------------------|
| `PORT`   | `5050`  | Port the server binds |
