# Buddy CLI

Buddy can be installed as a laptop command:

```bash
python3 tools/install_buddy_cli.py
```

After install:

```bash
buddy status
buddy setup
buddy test
buddy once
buddy full
buddy start
buddy stop
buddy dashboard
buddy open-test-kit
buddy song-test
buddy open-song-test
buddy open-website
buddy native-coverage
buddy native-report
buddy history-audit
buddy history-report
buddy router-refresh
buddy route coding
buddy route image_generation --mode local_only
buddy free-models
```

The CLI is free/local-first by default. It can scan, test, generate reports, open local files, start the local dashboard, and run guarded background maintenance. Live signups, secrets, money, deploys, outreach, account access, publishing, and destructive actions still require approval.

For media testing, `buddy song-test` creates a local song packet and `buddy open-song-test` opens a browser page where you can select your own image, select or record your own voice sample locally, and create a clone-readiness packet. The browser test previews and records files locally without uploading them; actual voice cloning stays gated until you approve a configured local model or approved provider for that specific use.

For native bot routing, `buddy native-coverage` scans the repository and proves which bot code can run first without another model. `buddy route <task>` now includes a `native_route` section so Buddy can try DreamCo bot code before optional free/local model help.

For recovery checks, `buddy history-audit` scans local clones, branches, and reflogs for recoverable work. It is non-destructive and only creates a report; compare candidate refs before merging or copying code.

For model routing, `buddy router-refresh` creates the professional API router and the top 100 free-first model/resource library. `buddy route <task>` shows the native bot route, then the free/local primary model and fallbacks Buddy can use only when helpful or selected.
