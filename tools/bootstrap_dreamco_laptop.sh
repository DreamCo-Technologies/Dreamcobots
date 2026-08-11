#!/usr/bin/env bash
set -euo pipefail

REPO_SLUG="DreamCo-Technologies/Dreamcobots"
DEFAULT_DIR="$HOME/Dreamcobots"
WORKDIR="${DREAMCO_DIR:-$DEFAULT_DIR}"
BACKEND_URL_DEFAULT="https://dreamco-buddy-312632932335.us-central1.run.app"

say() { printf '\n[%s] %s\n' "DreamCo" "$*"; }
warn() { printf '\n[DreamCo][WARN] %s\n' "$*" >&2; }
require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    warn "$1 is required but not installed."
    return 1
  fi
}

say "Checking laptop tools"
missing=0
for cmd in git node npm python3 gh; do
  require_cmd "$cmd" || missing=1
done
if [[ "$missing" -ne 0 ]]; then
  cat <<'TXT'
Install missing tools first. On macOS with Homebrew, typical commands are:
  brew install git node python gh
Then authenticate GitHub with:
  gh auth login
This script never prints or stores your tokens in the repository.
TXT
  exit 2
fi

say "Checking GitHub CLI authentication"
if ! gh auth status >/dev/null 2>&1; then
  warn "GitHub CLI is not authenticated. Run: gh auth login"
  exit 3
fi

if [[ ! -d "$WORKDIR/.git" ]]; then
  say "Cloning $REPO_SLUG into $WORKDIR"
  gh repo clone "$REPO_SLUG" "$WORKDIR"
else
  say "Using existing clone at $WORKDIR"
fi

cd "$WORKDIR"

say "Refreshing repository"
git fetch --all --prune
CURRENT_BRANCH="$(git branch --show-current || true)"
if [[ -z "$CURRENT_BRANCH" ]]; then
  git checkout main
fi
if git show-ref --verify --quiet refs/heads/main; then
  git checkout main >/dev/null 2>&1 || true
  git pull --ff-only origin main || warn "Local main has changes; skipped forced update."
fi

say "Preparing local environment file"
if [[ ! -f .env.local ]]; then
  if [[ -f .env.example ]]; then
    cp .env.example .env.local
    say "Created .env.local from .env.example"
  else
    : > .env.local
    say "Created empty .env.local"
  fi
fi
chmod 600 .env.local || true

set_env_key() {
  local key="$1"
  local value="$2"
  python3 - "$key" "$value" <<'PY'
from pathlib import Path
import sys
key, value = sys.argv[1], sys.argv[2]
path = Path('.env.local')
lines = path.read_text().splitlines() if path.exists() else []
found = False
out = []
for line in lines:
    if line.startswith(key + '='):
        out.append(f'{key}={value}')
        found = True
    else:
        out.append(line)
if not found:
    out.append(f'{key}={value}')
path.write_text('\n'.join(out).rstrip() + '\n')
PY
}

BACKEND_URL="${DREAMCO_BACKEND_URL:-$BACKEND_URL_DEFAULT}"
set_env_key "VITE_API_BASE_URL" "$BACKEND_URL"
set_env_key "DREAMCO_ALLOWED_ORIGINS" "http://localhost:5000,http://localhost:5173,https://dreamco-technologies.github.io"

say "Installing Node dependencies"
npm ci --ignore-scripts

say "Checking repository TypeScript"
npm run check

say "Testing backend health when reachable"
if command -v curl >/dev/null 2>&1; then
  if curl --silent --show-error --fail --max-time 10 "$BACKEND_URL/api/health" >/dev/null; then
    say "Backend health endpoint is reachable"
  else
    warn "Backend is not reachable at $BACKEND_URL yet. Local setup will still work."
  fi
fi

say "Checking optional deployment CLIs"
if command -v vercel >/dev/null 2>&1; then
  vercel whoami >/dev/null 2>&1 && say "Vercel CLI authenticated" || warn "Vercel CLI installed but not authenticated"
else
  warn "Vercel CLI not installed (optional)"
fi
if command -v gcloud >/dev/null 2>&1; then
  gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | grep -q . \
    && say "Google Cloud CLI authenticated" \
    || warn "Google Cloud CLI installed but no active account"
else
  warn "Google Cloud CLI not installed (optional)"
fi

say "Writing local connection report"
mkdir -p .dreamco
cat > .dreamco/laptop-status.txt <<EOF
DreamCo laptop bootstrap completed
Repository: $WORKDIR
Backend: $BACKEND_URL
GitHub CLI: authenticated
Node: $(node --version)
npm: $(npm --version)
Python: $(python3 --version 2>&1)
Generated: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
EOF

cat <<EOF

DreamCo laptop setup is ready.

Repository:
  $WORKDIR

Start the full local frontend + backend:
  cd "$WORKDIR"
  set -a; source .env.local; set +a
  npm run dev

Run repository checks:
  npm run test:repository

GitHub status:
  gh repo view $REPO_SLUG
  gh pr status

Important:
- Secrets stay in .env.local or provider secret stores, never in GitHub source.
- GitHub Pages uses the deployed backend URL; your laptop can use the same backend or the local server.
- Stripe, databases, model providers, Google APIs, Vercel, and Cloud services only become live when their own credentials are configured.
EOF
