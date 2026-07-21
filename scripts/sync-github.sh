#!/usr/bin/env bash
# DreamCo Empire OS — GitHub Auto-Sync Script
# Pushes all local commits to github.com/DreamCo-Technologies/Dreamcobots
# Safe to run anytime — reads token from environment, never stores it

set -euo pipefail

REPO="DreamCo-Technologies/Dreamcobots"
BRANCH="${DREAMCO_SYNC_BRANCH:-codex/recover-buddy-after-import}"

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "[sync] ❌ GITHUB_TOKEN not set — add it as an environment secret"
  exit 1
fi

REMOTE="https://${GITHUB_TOKEN}@github.com/${REPO}.git"
LOCAL_SHA=$(git --no-optional-locks rev-parse HEAD 2>/dev/null || echo "unknown")
LOCAL_MSG=$(git --no-optional-locks log -1 --pretty=format:"%s" 2>/dev/null || echo "unknown")

echo "[sync] 🚀 Pushing to github.com/${REPO}"
echo "[sync] 📌 Commit: ${LOCAL_SHA:0:7} — ${LOCAL_MSG}"

git --no-optional-locks push "$REMOTE" "HEAD:${BRANCH}" 2>&1 | grep -v "token\|password\|Authorization" || true

REMOTE_SHA=$(git --no-optional-locks ls-remote "$REMOTE" "$BRANCH" 2>/dev/null | cut -f1 | head -1 || echo "unknown")

if [ "${REMOTE_SHA:0:7}" = "${LOCAL_SHA:0:7}" ]; then
  echo "[sync] ✅ GitHub synced — $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "[sync]    Remote: ${REMOTE_SHA:0:7} = Local: ${LOCAL_SHA:0:7}"
else
  echo "[sync] ⚠️  SHA mismatch — remote: ${REMOTE_SHA:0:7} local: ${LOCAL_SHA:0:7}"
fi
