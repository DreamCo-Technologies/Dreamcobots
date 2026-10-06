# Fleet one-week build plan (Oct 6–12, 2026, CT)

Source of truth: `config/bots/build-queue.json` (checked by `tests/test_build_queue.py`). Starting point is the audit in #13731: 1232 bots (1213 TESTED, 19 SPEC_ONLY), all 55 App_bots divisions TESTED by the division smoke, 200 Pages (189 working, 10 stub, 1 broken), 105 workflows (90 runnable).

**Rules:** automation items never merge PRs, never flip production_ready/claimable/mastered, and never unblock money or destructive bots. Owner decisions are marked and wait for Irean.

| Day | Item | Kind | Owner | Done when |
|---|---|---|---|---|
| 10-06 | Review and merge #13729 (runtime contract, shared executor, generator) | **owner decision** | ireanjordan24 | `gh pr view 13729 --json state -q .state == MERGED` |
| 10-06 | Review and merge #13197 (Buddy control plane + /buddy router); confirm operators allowlist [ireanjordan24] | **owner decision** | ireanjordan24 | `gh pr view 13197 --json state -q .state == MERGED` |
| 10-06 | Retarget #13731 to main after #13729 merges; rerun Fleet runtime truth | automation | grok-bot | `python3 tools/fleet_runtime_audit.py --skip-folder-tests --check-regressions --no-write` |
| 10-07 | PR4: merge config/buddy/run-with-buddy.generated.json into the control-plane registry (curated jobs win); add /buddy customize to the router (allowlist + write permission, validate, branch + PR); Run/Customize/prospectus on buddy-control.html | automation | grok-bot | `python3 tools/build_actions_prospectus.py --check --check-buttons` |
| 10-07 | Review the 66 blocked_money bots (regex is over-inclusive, e.g. massage-therapist, landscaping-mgr); list the ones that should be runnable | **owner decision** | ireanjordan24 | `config/bots/run-policy-overrides.json exists and is reviewed` |
| 10-08 | Encode the owner's money-review decisions as explicit run-policy overrides in the generator (never auto-unblock) | automation | grok-bot | `python3 tools/generate_bot_manifests.py --check` |
| 10-08 | Give the 19 Markdown-only threejs-* bots a division source so UNASSIGNED stops being SPEC_ONLY (proposal PR, owner picks the division) | automation | grok-bot | `python3 -m buddy.fleet_runtime division-smoke --all` |
| 10-08 | Generate website/data/system-progress-status.json in CI (system-progress.html is the only 'broken' page) | automation | grok-bot | `python3 tools/audit_pages_features.py --check --check-regressions` |
| 10-09 | Wire or remove the 3 dead controls (bot-visual #run-sim, live-monitor #run-market, step-models form#task-form) | automation | grok-bot | `python3 tools/audit_pages_features.py --check --check-regressions` |
| 10-09 | For the 7 server-only pages (app-shop, buddy, connections, hf-unlock, models, search, sign-in): show a static 'needs the DreamCo server' state instead of failing silently | automation | grok-bot | `python3 tools/audit_pages_features.py --check --check-regressions` |
| 10-09 | Hand-written fixtures for one bot per division (55) so evidence is not only generated wiring checks | automation | grok-bot | `python3 -m buddy.fleet_runtime smoke --all` |
| 10-10 | Decide whether to add model-gateway secrets for live (CONNECTED) runs; names only, never values in the repo | **owner decision** | ireanjordan24 | `secret names listed in docs/UNIVERSAL_BOT_RUNTIME_CONTRACT.md` |
| 10-10 | Fix runtime/ folder tests (verdict broken) and buddy_os capability batch import assertion | automation | grok-bot | `FULL=1 bash tools/regen_fleet_truth.sh` |
| 10-11 | Stop folder tests writing into the checkout (folder_test_side_effects in the audit) | automation | grok-bot | `FULL=1 bash tools/regen_fleet_truth.sh && git diff --exit-code` |
| 10-11 | If secrets were approved: first CONNECTED evidence run for one bot per engine via fleet-bot-run.yml | automation | grok-bot | `python3 tools/fleet_runtime_audit.py --skip-folder-tests --check-regressions --no-write` |
| 10-12 | Weekly truth report: per-division states, pages verdicts, what moved, what is still stub | automation | grok-bot | `bash tools/regen_fleet_truth.sh` |

## Registering the queue as a Buddy job (after #13197 merges)

1. Add a `fleet_build_queue_status` job to `config/buddy/control-plane.json` (read_only tier, workflow `fleet-runtime-truth.yml`, no inputs).
2. Operators comment `/buddy run fleet_build_queue_status` on an issue. The router dispatches the truth workflow, and the summary artifact shows which acceptance checks pass.
3. Item status is updated by PR only (edit `status` in `config/bots/build-queue.json`). Nothing is marked done without its acceptance command passing.
