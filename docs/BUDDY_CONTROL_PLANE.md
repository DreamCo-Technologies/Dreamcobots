# Buddy Control Plane

Goal from the owner (2026-10-03): everything Grok bots or GitHub Actions do for DreamCo,
Buddy can do on its own, and it can be managed, controlled, or triggered by Buddy from
GitHub Pages.

The control plane has five parts:

| Part | File | What it does |
|---|---|---|
| Registry | `config/buddy/control-plane.json` | Every Buddy-runnable job: workflow file, allowed inputs, risk tier, owner approval, triggerable or blocked (with reason). Also `operators` and `owners`. |
| Router | `.github/workflows/buddy-command-router.yml` | Reads `/buddy ...` commands from issues and issue comments, checks who sent them, validates against the registry, dispatches the workflow, comments back. |
| Library + CLI | `tools/buddy_control_plane.py` | Parser, validator, auth decision, registry schema check, status snapshot. Tests: `tests/test_buddy_control_plane.py`. |
| Status snapshot | `website/data/buddy-control-status.json` | Last run per registered workflow on `main`, written at every Pages build (push to `main` and twice a day by schedule). No secrets. |
| Control panel | `website/buddy-control.html` (+ `buddy-control.js`) | Lists every job with status, last run, **Run with Buddy**, **View workflow**, **Open Actions**. Static: it holds no tokens and runs nothing itself. |

## How a run works

1. On the Control Panel, press **Run with Buddy**. It opens a prefilled GitHub issue:
   title `/buddy run <job_id>`, label `buddy-command`, and a body with a fenced block:

   ````text
   ```buddy-inputs
   mode=quick
   ```
   ````

2. Submitting the issue fires `buddy-command-router.yml` (`issues: opened/labeled`).
   You can also comment on any issue (not PRs):

   ```text
   /buddy list
   /buddy status [job_id]
   /buddy run <job_id> [key=value ...]
   /buddy help
   ```

3. The router (runs from the default branch, never from a PR):
   * parses the first line strictly (ASCII, `/buddy <verb>`, job id `^[a-z][a-z0-9_]{1,63}$`,
     inputs `key=value` with key `^[a-z][a-z0-9_]{0,39}$` and value `^[A-Za-z0-9._-]{1,100}$`);
   * checks the sender is in `operators` **and** has write/maintain/admin on the repo
     (`GET /repos/{repo}/collaborators/{user}/permission`). For issue commands the issue
     author must also be an operator;
   * checks the job exists, is `triggerable`, is not `money` tier, is not `destructive`;
     owner-approval jobs need a sender in `owners`;
   * validates each input against the job's spec (choice / boolean / anchored pattern),
     applies defaults, and forces `fixed_inputs` (which cannot be overridden);
   * dispatches with `gh workflow run <file> --ref main -f key=value ...` (argument list,
     no shell) using the job's `GITHUB_TOKEN` (`actions: write`, `issues: write`, `contents: read`);
   * comments back with the run URL, or with the reason it rejected the command.

Commands from issues are handled once even though GitHub sends both `opened` and
`labeled` for a new labeled issue (the router looks for its own marker comment).

## Security model

* **Pages is public and static.** No tokens, no API writes from the browser. The page only
  builds GitHub URLs. "Refresh live" uses GitHub's anonymous public API (60 requests/hour).
* **Strict allowlist.** Only registry jobs, only declared inputs, only on `default_ref`.
  The ref is never caller-chosen.
* **No shell interpolation of user text.** Issue/comment text reaches the router only as
  env vars and is parsed in Python. The only `run:` line in the router is
  `python3 tools/buddy_control_plane.py route`. Rejection comments never echo raw input.
* **Two-factor authorization.** Registry `operators` (seed: `ireanjordan24`) **and** live
  repo write permission. Bots are rejected.
* **Fail closed.** If the registry fails validation, the permission lookup fails, or the
  API errors, nothing is dispatched. Unavailable status is shown as `unavailable`, not green.
* **Never from Pages or the router:** `money` tier (payments, Stripe, revenue), anything
  `destructive` (deletes or bulk-closes), anything that pushes code to `main`, and anything
  that could flip `production_ready` / `claimable`.
* **`writes_code` jobs must be PR-only.** `check` rejects a triggerable `writes_code` job
  whose workflow has a bare `git push` / push to `main`. `branch_health_resolve` is blocked
  for that reason until its report step opens a PR.
* **Least privilege.** Router job permissions are exactly `actions: write`, `issues: write`,
  `contents: read`; workflow-level `permissions: {}`. Actions are pinned by commit SHA. No
  `pull_request_target`.
* A `read_only` job must point at a workflow whose token cannot write (checked by `check`).

## Risk tiers

| Tier | Meaning | Router |
|---|---|---|
| `read_only` | Token is read-only; output is logs, step summary, artifacts. | Any operator |
| `writes_reports` | May open/comment issues, publish Pages, or commit generated reports/data. | Any operator; owner if `requires_owner_approval` |
| `writes_code` | Changes code/branches. PR-only, never pushes to `main`. | Owner only |
| `money` | Payments, Stripe, payouts, pricing, revenue. | Never |

## Adding a job

1. Pick (or, only if none exists, add) a workflow with a `workflow_dispatch` trigger.
2. Add an entry under `jobs` in `config/buddy/control-plane.json`:

   ```json
   {
     "id": "my_job",
     "family": "system watch",
     "title": "Human-readable title",
     "workflow": "my-workflow.yml",
     "risk_tier": "read_only",
     "requires_owner_approval": false,
     "triggerable": true,
     "inputs": {
       "mode": {"type": "choice", "options": ["quick", "full"], "default": "quick"}
     },
     "fixed_inputs": {},
     "notes": "optional"
   }
   ```

   Input types: `choice` (options), `boolean`, `string` (needs an anchored `pattern` and
   `max_length` <= 100). Every input must be declared in the workflow's `workflow_dispatch.inputs`.
   Blocked jobs set `"triggerable": false` and a `blocked_reason`.
3. Run:

   ```bash
   python3 tools/buddy_control_plane.py check            # schema + workflow cross-check (needs PyYAML)
   python3 tools/buddy_control_plane.py publish-registry # refresh website/data/buddy-control-plane.json
   python3 -m unittest tests.test_buddy_control_plane
   ```

## Adding an operator

Add the GitHub login to `operators` (and to `owners` only for owner-level control). The
person must also have write access to the repository; the registry alone is not enough.

## How Buddy (the in-app agent) can call the same router

Not wired yet; the `/api` auth change (PR #13195) is pending. When it lands, the server-side
path should be:

1. Buddy calls `POST /api/github/trigger-workflow` **only behind authenticated owner/operator
   sessions** (the PR #13195 middleware), with `{ "job_id": "...", "inputs": { ... } }`, never a
   raw workflow file name.
2. The handler loads the same `config/buddy/control-plane.json`, and applies the same rules as
   `tools/buddy_control_plane.py`: `validate_run` (job exists, triggerable, not money, not
   destructive, inputs allowlisted, fixed inputs forced) and `authorize` (signed-in user mapped
   to a GitHub login that is an operator with write permission; owners for owner-approval jobs).
3. It dispatches `ref: default_ref` with only the validated inputs, and records who asked.
   Simplest equivalent: have the server post `/buddy run <job_id> ...` as a comment on a
   dedicated tracking issue, so every Buddy-initiated run goes through the router and leaves an
   audit trail.

Current state to fix before wiring: today `POST /api/github/trigger-workflow` in
`server/routes.ts` has no auth check, accepts any workflow file name from the request body,
and always sends `era/mode/deep_buddy` inputs. It must not be exposed as the Buddy path until
it requires auth and uses this registry.

## Status snapshot

`python3 tools/buddy_control_plane.py status --out website/data/buddy-control-status.json`
reads `GET /repos/{repo}/actions/workflows/{file}/runs?branch=main&per_page=1` per registered
workflow and keeps only state, run URL (validated), run number, event, and time. It runs in
`deploy-buddy-pages.yml` (push to `main` + `47 5,17 * * *` UTC). States: `success`, `failure`,
`in_progress`, `queued`, `cancelled`, `never_run`, `workflow_missing`, `unavailable`.

## One-time setup

Create the command label once (the router also accepts new issues whose title starts with
`/buddy ` without it):

```bash
gh label create buddy-command --repo DreamCo-Technologies/Dreamcobots --color 5319e7 \
  --description "Buddy control-plane command (see docs/BUDDY_CONTROL_PLANE.md)"
```

## Generated jobs and `/buddy customize` (fleet runtime integration)

**Generated jobs.** `tools/build_actions_prospectus.py` (#13731) writes `config/buddy/run-with-buddy.generated.json`. It has one job per workflow, plus `fleet_bot_run` and `fleet_division_run`. The router merges these jobs under the curated registry (`merge_generated`):

- A curated job always wins, whether it matches on id or on workflow.
- Each generated job must pass `check_registry` by itself. A bad generated job is skipped. It never invalidates the curated registry, and if the file is unreadable the router uses curated jobs only.
- The router reads the file through its sparse checkout. `python3 tools/buddy_control_plane.py check` lists every skipped generated job and why.
- `publish-registry` still publishes curated jobs only. `buddy-control.html` renders the generated jobs (with their prospectus) from `website/data/run-prospectus.json` when that file is deployed.

**Customize.** Write `/buddy customize <bot-id|division:Name|file:path>` as the issue title or the first line of a comment, then add exactly one fenced `yaml` patch. The Pages Customize forms open this issue already filled in.

1. The router checks the target syntax and the patch structure (one fence, at most 4000 characters, no control characters). It applies the same authorization as `run`: an operator with write permission, an operator as issue author, and owner approval because the apply job is `writes_code`. Then it dispatches `buddy-customize-apply.yml` with only `issue` and `comment` ids as inputs.
2. `tools/buddy_customize_apply.py` re-reads the request from the API (never from inputs). It re-checks the author and their permission, then runs the allowlist validator:
   - `python -m buddy.fleet_runtime customize --apply` for bots and divisions
   - `tools/build_file_prospectus.py customize --apply` for files
   It fails if any file other than `config/bots/customizations.json` or `config/files/prospectus-overrides.json` changed.
3. The workflow commits to `buddy/customize-<issue>-<run>`, opens a PR and comments the PR link on the issue (the "pending change"). It never pushes to the default branch and never merges.

Requirements:
- The fleet runtime (#13729, #13731) must be on the default branch.
- For the workflow to open the PR itself, an owner must enable *Settings → Actions → Allow GitHub Actions to create and approve pull requests*. Without it, the workflow comments a compare link instead.
- PRs opened with `GITHUB_TOKEN` don't trigger CI on their own. Re-run the checks or push an empty commit before merging.
