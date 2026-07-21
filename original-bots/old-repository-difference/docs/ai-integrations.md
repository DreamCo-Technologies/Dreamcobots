# AI Service Integrations

This document explains how to connect Dreamcobots to **Claude (Anthropic)**,
**ChatGPT (OpenAI)**, **Google Gemini**, and **DreamCo** using GitHub Actions
and repository secrets.

---

## Overview

| Service | Secret name | Docs |
|---------|-------------|------|
| Claude (Anthropic) | `CLAUDE_API_KEY` | <https://docs.anthropic.com> |
| ChatGPT (OpenAI) | `CHATGPT_API_KEY` | <https://platform.openai.com/docs> |
| Google Gemini | `GEMINI_API_KEY` | <https://ai.google.dev/docs> |
| GitHub PAT | `GITHUB_PAT` | <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens> |

The workflow file is at
`.github/workflows/ai-service-integration.yml` and runs automatically on:

- every push to the `main` branch, and
- pull requests that have the `ai-review` label applied.

It can also be triggered manually from the **Actions** tab via
*workflow_dispatch*.

---

## 1 — Obtain API keys

### Claude (Anthropic)
1. Sign in at <https://console.anthropic.com>.
2. Go to **API Keys** and click **Create Key**.
3. Copy the key — it starts with `sk-ant-…`.

### ChatGPT (OpenAI)
1. Sign in at <https://platform.openai.com>.
2. Go to **API Keys** and click **Create new secret key**.
3. Copy the key — it starts with `sk-…`.

### Google Gemini
1. Sign in at <https://aistudio.google.com>.
2. Click **Get API key** → **Create API key**.
3. Copy the key.

### GitHub Personal Access Token (PAT)
1. Go to <https://github.com/settings/tokens>.
2. Click **Generate new token (fine-grained)**.
3. Under **Repository access** select *DreamCo-Technologies/Dreamcobots*.
4. Grant **Contents** (read) and **Workflows** (read & write) permissions.
5. Click **Generate token** and copy the value.

> **Security note:** Never commit API keys or tokens to source control.  Use
> GitHub Actions secrets or a secrets manager (e.g. AWS Secrets Manager,
> HashiCorp Vault).

---

## 2 — Add secrets to the repository

### Via the GitHub UI
1. Open the repository on GitHub.
2. Go to **Settings → Secrets and variables → Actions**.
3. Click **New repository secret** for each entry:

| Name | Value |
|------|-------|
| `GITHUB_PAT` | your GitHub Personal Access Token |
| `CLAUDE_API_KEY` | your Anthropic API key |
| `CHATGPT_API_KEY` | your OpenAI API key |
| `GEMINI_API_KEY` | your Google AI API key |

### Via the `gh` CLI
```bash
gh secret set GITHUB_PAT      --body "paste-your-github-token"
gh secret set CLAUDE_API_KEY  --body "sk-ant-..."
gh secret set CHATGPT_API_KEY --body "sk-..."
gh secret set GEMINI_API_KEY  --body "paste-your-google-ai-key"
```

---

## 3 — Workflow behaviour

When the workflow runs it:

1. **Checks out** the repository.
2. **Calls Claude** — sends a short prompt to
   `https://api.anthropic.com/v1/messages` and prints the response.
3. **Calls ChatGPT** — sends a short prompt to
   `https://api.openai.com/v1/chat/completions` and prints the response.
4. **Calls Google Gemini** — sends a short prompt to the Gemini 1.5 Flash
   endpoint (key passed via `x-goog-api-key` header) and prints the response.
5. Each step **skips gracefully** if its secret is not configured, so the
   workflow never fails just because a single key is missing.

Adapt the prompt strings inside each `curl` call to suit your use-case (e.g.
pass repo metadata, file diffs, or issue text as context).

---

## 4 — Local development

Create a `.env` file in the repo root (already listed in `.gitignore`):

```dotenv
CLAUDE_API_KEY=sk-ant-...
CHATGPT_API_KEY=sk-...
GEMINI_API_KEY=paste-your-google-ai-key
GITHUB_PAT=paste-your-github-token
```

Then load it before running scripts:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 5 — DreamCo integration

DreamCo can sync with this repository so that changes pushed to `main` are
automatically reflected in your DreamCo project.

### Connect DreamCo to GitHub
1. Open your DreamCo project.
2. Click the **Version control** icon (branch icon) in the left sidebar.
3. Click **Connect to GitHub** and authorise the DreamCo GitHub App.
4. Select the `DreamCo-Technologies/Dreamcobots` repository.
5. Choose whether DreamCo should pull from `main` automatically or on demand.

### Add secrets to DreamCo
DreamCo projects use **Secrets** (environment variables) instead of `.env`
files for security.

1. In your DreamCo project, open the **Secrets** tab (lock icon).
2. Add each key:

| Key | Value |
|-----|-------|
| `GITHUB_PAT` | your GitHub Personal Access Token |
| `CLAUDE_API_KEY` | your Anthropic API key |
| `CHATGPT_API_KEY` | your OpenAI API key |
| `GEMINI_API_KEY` | your Google AI API key |

3. Your code can read them with `os.environ["CLAUDE_API_KEY"]` (Python) or
   `process.env.CLAUDE_API_KEY` (Node.js).

### Keep DreamCo in sync
- **Push from DreamCo → GitHub**: use the **Commit & push** button in the
  Version control panel.
- **Pull from GitHub → DreamCo**: click **Pull** in the Version control panel,
  or enable *Auto-pull on run* in project settings.

---

## 6 — Trigger the workflow manually

```bash
# Requires gh CLI and the GITHUB_PAT to be configured
gh workflow run ai-service-integration.yml --repo DreamCo-Technologies/Dreamcobots
```

Or open **Actions → AI Service Integration → Run workflow** in the GitHub UI.
