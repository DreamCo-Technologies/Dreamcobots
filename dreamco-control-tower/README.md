# 🏰 DreamCo Control Tower

**Centralized bot management hub** for the DreamCo empire — integrated with GitHub for fully autonomous bot operations, monitoring, updates, and analytics.

---

## Directory Structure

```
dreamco-control-tower/
├── backend/
│   ├── server.js              # Express.js API (heartbeat + GitHub webhooks)
│   └── api/
│       ├── bot-manager.js     # Bot registry (read/write bots.json)
│       ├── repo-manager.js    # GitHub PR, commit, and workflow monitoring
│       └── revenue-tracker.js # Payment event recording and aggregation
├── frontend/
│   ├── src/
│   │   ├── App.jsx                        # Root layout with sidebar navigation
│   │   ├── main.jsx                       # React entry point
│   │   ├── index.css                      # Tailwind base styles
│   │   └── components/
│   │       ├── BotOverview.jsx            # Live bot status + heartbeat
│   │       ├── RepoActivity.jsx           # GitHub PRs, commits, workflow status
│   │       ├── BotDeployment.jsx          # Deploy new bots from templates
│   │       ├── Analytics.jsx              # Uptime, PR trends, status charts
│   │       ├── ActionsPage.jsx            # Actions monitor + Buddy launcher modal
│   │       ├── BuddyCommandCenter.jsx     # Full Buddy command center modal content
│   │       └── CommandCenter.jsx          # Max-parallel lane board + June 22 plan
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── automation/
│   └── auto-upgrade-bots.js   # Pull latest, resolve conflicts, open PRs
├── scripts/
│   └── heartbeat-check.js     # CLI report of all bot heartbeat ages
├── config/
│   ├── bots.json              # Bot registry (name, repo, status, heartbeat)
│   ├── command_center.json    # Must-ship scope, lane ownership, and timeline
│   ├── users.json             # Access control records
│   └── payments.json          # Stripe/PayPal key placeholders
└── package.json               # Backend dependencies
```

---

## Features

### 1️⃣ Heartbeat Monitoring
Every bot POSTs to `/api/bot-heartbeat` to signal it is alive. The Control Tower records the timestamp and flags bots as **stale** if no heartbeat is received within 5 minutes.

### 2️⃣ GitHub Webhook Integration
`/api/github-webhook` receives GitHub events:
- **pull_request** – tracks PR open/merge actions
- **issues** – triggers auto-heal when an issue is labeled `bug`
- **workflow_run** – alerts on failed CI workflows
- **push** – logs commit activity

### 3️⃣ Auto-Upgrade Automation
`automation/auto-upgrade-bots.js` iterates all registered bots and:
1. Pulls the latest `main` branch changes (`git pull --rebase`)
2. Auto-resolves conflicts using the `merge -X theirs` strategy
3. Runs optional npm tests
4. Opens a pull request via the GitHub API for any upgrades

### 4️⃣ Frontend Dashboard (React + Tailwind)
| View | Description |
|------|-------------|
| **Bot Overview** | Live status, last heartbeat, workflow result, open PRs |
| **Repo Activity** | GitHub commits, PR merges, open PRs, workflow results |
| **Bot Deployment** | Create and deploy bots from templates with one click |
| **Analytics** | Uptime charts, PR success rates, status distribution |
| **Actions** | GitHub Actions monitor plus a launchable Buddy terminal modal for autonomous command dispatch |
| **Command Center** | Must-ship scope, lane owners, blockers, validation, ship decisions, and swarm/MARL benchmark telemetry |

---

## Getting Started

### Backend

```bash
cd dreamco-control-tower
npm install
# Set env vars
export GITHUB_TOKEN=your_token
export PORT=4000
npm start
```

### Frontend

```bash
cd dreamco-control-tower/frontend
npm install
npm run dev   # Opens on http://localhost:5173
npm run test  # Runs Actions/Buddy UI tests (modal + Enter key flows)
```

### Heartbeat Check (CLI)

```bash
npm run heartbeat
```

### Auto-Upgrade All Bots

```bash
npm run upgrade
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token (repo scope) | Yes for GitHub API calls |
| `GITHUB_OWNER` | GitHub username or org (default: `ireanjordan24`) | No |
| `PORT` | API server port (default: `4000`) | No |
| `STRIPE_KEY` | Stripe secret key for revenue tracking | Optional |
| `STALE_MINUTES` | Minutes before a bot is flagged stale (default: `5`) | No |

---

## Configuration

### `config/bots.json`
Each entry describes a registered bot:
```json
{
  "name": "affiliate-bot",
  "repoName": "Dreamcobots",
  "repoPath": "./bots/affiliate_bot",
  "branch": "main",
  "lastHeartbeat": null,
  "status": "idle",
  "lastPR": null,
  "workflowStatus": "unknown"
}
```

---

## Deployment

| Layer | Recommended Platform |
|-------|----------------------|
| Frontend | Vercel / Netlify |
| Backend API | AWS Lambda / Heroku / Render |
| Database (scale) | MongoDB Atlas (replace `bots.json` reads with Mongoose) |

---

## Python Integration

The Python `bots/control_center/control_center.py` has been extended with:
- `record_heartbeat(bot_name, status)` — record a bot heartbeat
- `get_heartbeat_status()` — query all heartbeat ages
- `get_stale_bots()` — list bots with stale heartbeats
- `handle_github_event(event, payload)` — process GitHub webhook events
- `get_webhook_log(limit)` — retrieve recent webhook events
