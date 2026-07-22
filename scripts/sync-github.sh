#!/usr/bin/env bash
# DreamCo Empire OS - GitHub Review-Branch Sync Script
# Pushes all local commits to github.com/DreamCo-Technologies/Dreamcobots
# Reads the token from the environment and never places it in a remote URL.

set -euo pipefail

REPO="DreamCo-Technologies/Dreamcobots"
BRANCH="${BUDDY_GITHUB_SYNC_BRANCH:-buddy/automated-updates}"
TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN:-${GITHUB_TOKEN:-}}"

if [ -z "$TOKEN" ]; then
  echo "[sync] GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_TOKEN is not set"
  exit 1
fi

if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "[sync] Refusing to write directly to the protected default branch"
  exit 1
fi

REMOTE="https://github.com/${REPO}.git"
LOCAL_SHA=$(git --no-optional-locks rev-parse HEAD 2>/dev/null || echo "unknown")
LOCAL_MSG=$(git --no-optional-locks log -1 --pretty=format:"%s" 2>/dev/null || echo "unknown")

echo "[sync] Pushing to github.com/${REPO} branch ${BRANCH}"
echo "[sync] Commit: ${LOCAL_SHA:0:7} - ${LOCAL_MSG}"

GIT_CONFIG_COUNT=1 \
GIT_CONFIG_KEY_0=http.https://github.com/.extraheader \
GIT_CONFIG_VALUE_0="Authorization: Bearer ${TOKEN}" \
git --no-optional-locks push "$REMOTE" "HEAD:refs/heads/${BRANCH}"

REMOTE_SHA=$(GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.https://github.com/.extraheader GIT_CONFIG_VALUE_0="Authorization: Bearer ${TOKEN}" git --no-optional-locks ls-remote "$REMOTE" "$BRANCH" 2>/dev/null | cut -f1 | head -1 || echo "unknown")

if [ "${REMOTE_SHA:0:7}" = "${LOCAL_SHA:0:7}" ]; then
  echo "[sync] GitHub synced - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "[sync]    Remote: ${REMOTE_SHA:0:7} = Local: ${LOCAL_SHA:0:7}"
else
  echo "[sync] SHA mismatch - remote: ${REMOTE_SHA:0:7} local: ${LOCAL_SHA:0:7}"
fi
