# DreamCo Laptop Control Hub

This setup makes a laptop the local DreamCo development and control environment without committing credentials to GitHub.

## One-command bootstrap

From Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/DreamCo-Technologies/Dreamcobots/main/tools/bootstrap_dreamco_laptop.sh -o /tmp/bootstrap_dreamco_laptop.sh
bash /tmp/bootstrap_dreamco_laptop.sh
```

If the bootstrap change is still on a pull-request branch rather than `main`, clone the repository with GitHub CLI and run the script from that branch instead:

```bash
gh repo clone DreamCo-Technologies/Dreamcobots ~/Dreamcobots
cd ~/Dreamcobots
git fetch origin agent/github-pages-full-page-coverage
git checkout agent/github-pages-full-page-coverage
bash tools/bootstrap_dreamco_laptop.sh
```

## What it connects

- GitHub repository and GitHub CLI
- local React frontend
- local Express/Node backend
- the configured deployed DreamCo backend
- local `.env.local` configuration
- Node/npm and Python runtime checks
- optional Vercel CLI authentication status
- optional Google Cloud CLI authentication status

## What still requires provider credentials

A local clone cannot manufacture service credentials. Stripe, databases, OpenAI/model providers, Google Maps APIs, Vercel resources, Google Cloud resources, email, storage, and similar external systems require the corresponding user-owned key, OAuth connection, or provider login.

Store these only in `.env.local`, Vercel environment variables, Google Cloud Secret Manager, GitHub Actions secrets/variables, or the relevant provider secret store. Never commit secret values.

## Start DreamCo locally

```bash
cd ~/Dreamcobots
set -a
source .env.local
set +a
npm run dev
```

By default the server listens on port 5000 unless `PORT` is set.

## Verify

```bash
curl http://localhost:5000/api/health
npm run check
npm run test:repository
gh pr status
```

## GitHub Pages relationship

GitHub Pages is static hosting. The repository's Pages build publishes the static `website/` system plus the full React app under `/app/`, and the React app forwards backend calls to `VITE_API_BASE_URL`.

The laptop can run the same backend locally, but the public Pages site should target a separately deployed HTTPS backend. Cross-origin access is limited by the backend's configured allowed origins.

## Local status report

The bootstrap writes `.dreamco/laptop-status.txt`. The `.dreamco` folder is intended for local machine status only and must not contain secrets or be treated as a cloud credential store.
