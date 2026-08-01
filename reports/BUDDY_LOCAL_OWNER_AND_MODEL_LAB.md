# Buddy Local Owner Workspace and Model Lab

## Working Now

- Buddy can be served from a loopback-only laptop bridge with an ephemeral session token.
- The local bridge can open an approved browser search, HTTPS address, or allowlisted app after one visible approval.
- Pause and resume controls apply immediately and the last 50 redacted action events remain in memory only.
- Creative Studio can record up to 60 seconds of owner audio, take a camera image, preview both locally, and export each source file.
- Creative Studio generates a portable consent receipt containing SHA-256 fingerprints rather than raw biometric media.
- The generated benchmark catalog contains exactly 100 targets, 89 providers, 17 categories, and 12 evaluation suites.
- The local catalog audit validates identity, task-fit, access, capability, instruction, and suite metadata without calling a provider.

## Start the Laptop Workspace

```bash
python3 tools/buddy_cli.py local-start
```

The command opens a private link similar to `http://127.0.0.1:8765/buddy.html#buddy-local-token=...`. The token is kept in browser session storage and removed from the visible address.

## Security Contract

- Loopback binding only
- Short-lived session token
- No raw credentials accepted
- HTTPS destinations only, except loopback development addresses
- One-action approval for every browser or app launch
- No arbitrary background clicks, typing, sign-ins, submissions, purchases, or publishing
- Immediate pause control
- Memory-only redacted audit log

## Benchmark Evidence Contract

A catalog-ready target is not the same as a live-tested model. A live result must include the exact provider and model id, fixture hash, redacted response hash, latency, retries, token usage when available, actual cost when available, grader version, and UTC timestamp.

Paid runs require an explicit maximum spend and approval for that run. The static public site prepares plans but never calls a paid provider.

## External Adapter Boundary

Buddy Native provides local routing, planning, catalog audits, media capture, and task packets. Provider inference, remote app writes, cross-device control, media rendering, and third-party publishing still require an authenticated adapter that follows the owner approval policy.
