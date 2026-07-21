# DreamCo Money Operating System — Setup Guide

This guide covers everything you need to get the DreamCo Money Operating System running — from a fresh machine to a fully operational money-making automation platform.

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Runs the API, dashboard, and bot scheduler |
| npm | 9+ | Dependency management |
| Python | 3.9+ | Runs the Python-based bots |
| Docker | 20+ | Optional containerized deployment |
| Docker Compose | 2+ | Optional multi-service orchestration |
| Git | Any | Clone the repository |

### Optional (Recommended)

- **PostgreSQL 14+** — Production database (SQLite-compatible schema included)
- **Redis** — Queue backend for high-volume bot runs
- **Stripe Account** — Payment processing
- **OpenAI API Key** — AI-powered proposal drafting, lead scoring

### System Requirements

- **RAM**: 2 GB minimum, 4 GB recommended
- **CPU**: 2 cores minimum
- **Disk**: 5 GB free space
- **OS**: Linux (Ubuntu 22.04+), macOS 12+, or Windows 11 with WSL2

---

## 1. Clone the Repository

```bash
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git
cd Dreamcobots
```

---

## 2. Install Node.js Dependencies

```bash
npm install
```

This installs:
- `express` — HTTP server
- `dotenv` — Environment variable loading

Dev dependencies (ESLint, Jest, Prettier) are also installed automatically.

---

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or with a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

---

## 4. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` with your values. Here are the most important variables:

### Application Settings

```env
NODE_ENV=development           # development | staging | production
PORT=3000                      # Main HTTP server port
API_PORT=3001                  # API server port
LOG_LEVEL=INFO                 # DEBUG | INFO | WARN | ERROR | CRITICAL
SECRET_KEY=your_random_secret  # Change this! Use openssl rand -hex 32
```

### Database

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dreamco
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dreamco
DB_USER=postgres
DB_PASSWORD=your_password
DB_POOL_SIZE=10
```

For development without PostgreSQL, the system uses an in-memory store automatically.

### Stripe Payments

```env
# Paste your Stripe secret key from dashboard.stripe.com.
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...      # From Stripe Dashboard → Webhooks
```

### OpenAI (for AI features)

```env
OPENAI_API_KEY=sk-...                # Get from platform.openai.com
OPENAI_MODEL=gpt-4o-mini             # Model to use
```

### Cron Scheduler

```env
CRON_ENABLED=true
BOT_RUN_INTERVAL_MS=3600000          # Every hour
LEAD_SCRAPE_INTERVAL_MS=21600000     # Every 6 hours
EMAIL_SEND_INTERVAL_MS=86400000      # Daily
```

---

## 5. Database Setup

### Option A: Skip (Development / In-Memory)

No setup required. The system automatically uses an in-memory store for development.

### Option B: PostgreSQL

1. Install PostgreSQL:
   ```bash
   sudo apt install postgresql postgresql-contrib   # Ubuntu
   brew install postgresql@14                        # macOS
   ```

2. Create the database:
   ```bash
   psql -U postgres -c "CREATE DATABASE dreamco;"
   psql -U postgres -c "CREATE USER dreamco_user WITH PASSWORD 'yourpassword';"
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE dreamco TO dreamco_user;"
   ```

3. Run the initial migration:
   ```bash
   psql -U dreamco_user -d dreamco -f database/migrations/001_initial.sql
   ```

4. Verify:
   ```bash
   psql -U dreamco_user -d dreamco -c "\dt"
   # Should show: users, leads, deals, automation_logs, revenue, bot_schedules
   ```

---

## 6. Running Locally

### Start the Main Server

```bash
npm start
```

The server will be available at:
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:3000/api
- **Health check**: http://localhost:3000/health

### Run Tests

```bash
npm test
```

### Lint

```bash
npm run lint
npm run lint:fix   # Auto-fix lint errors
```

### Start the Python Orchestrator

```bash
python core/dreamco_orchestrator.py
```

### Run a Single Bot (Python)

```bash
python bots/lead_scraper/multi_source_lead_scraper.py
```

---

## 7. Running with Docker

### Build and Start All Services

```bash
docker-compose up --build
```

This starts:
- **dreamcobots** — Node.js API + dashboard (port 3000)
- **postgres** — PostgreSQL database (port 5432)
- **redis** — Redis cache (port 6379)
- **grafana** — Monitoring dashboard (port 3001)

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f dreamcobots
```

### Build Docker Image Only

```bash
docker build -t dreamcobots:latest .
```

---

## 8. Verifying the Setup

### Check Server Health

```bash
curl http://localhost:3000/health
# Expected: {"status":"ok","service":"dreamcobots","uptime":...}
```

### Check Bot Catalog

```bash
curl http://localhost:3000/bots | python3 -m json.tool | head -30
# Expected: {"bots":[...],"total":N}
```

### Check API Status

```bash
curl http://localhost:3000/api/status
# Expected: {"status":"ok","bots":...,"revenue":...}
```

### Open the Dashboard

Navigate to http://localhost:3000 in your browser. You should see the DreamCo admin dashboard with:
- Summary cards (Revenue, Bots, Leads, Deals)
- Revenue chart
- Bot status table
- Lead table
- Workflow pipeline cards

---

## 9. Production Deployment

### Environment Variables for Production

Set `NODE_ENV=production` and ensure all secret keys are real (not test values).

### Railway (Recommended)

1. Push your code to GitHub
2. Connect the repo at [railway.app](https://railway.app)
3. Add environment variables in the Railway dashboard
4. Railway auto-deploys on every push

```bash
# One-time Railway CLI deploy
npm install -g @railway/cli
railway login
railway link
railway up
```

### Heroku

```bash
heroku create dreamco-app
heroku addons:create heroku-postgresql:mini
heroku config:set NODE_ENV=production
heroku config:set STRIPE_SECRET_KEY=
git push heroku main
```

### Manual VPS (Ubuntu)

```bash
# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Clone and install
git clone https://github.com/DreamCo-Technologies/Dreamcobots.git /opt/dreamcobots
cd /opt/dreamcobots && npm install --production

# Create systemd service
sudo tee /etc/systemd/system/dreamcobots.service << EOF
[Unit]
Description=DreamCo Money OS
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/dreamcobots
ExecStart=/usr/bin/node index.js
Restart=always
EnvironmentFile=/opt/dreamcobots/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable dreamcobots
sudo systemctl start dreamcobots
sudo systemctl status dreamcobots
```

---

## 10. Troubleshooting

### Port Already in Use

```bash
# Find what's using port 3000
lsof -i :3000
kill -9 <PID>
```

### Database Connection Refused

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Tests Failing

```bash
# Clear Jest cache
npx jest --clearCache
npm test
```

### Python Bot Errors

```bash
# Ensure venv is activated
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## Next Steps

- Read [BOT_GUIDE.md](./BOT_GUIDE.md) to learn how to configure and run individual bots
- Read [MONEY_GUIDE.md](./MONEY_GUIDE.md) to understand all revenue streams
- Read [workflows/README.md](./workflows/README.md) to understand the workflow engine
