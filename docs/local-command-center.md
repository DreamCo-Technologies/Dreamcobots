# DreamCo Local Command Center

The M5 Mac should act as Buddy's local execution workstation while GitHub remains the source of truth.

## First setup

```bash
cd ~/DreamCo/Dreamcobots
chmod +x tools/dreamco_command_center.sh
./tools/dreamco_command_center.sh
```

## Design goals

- Pull current GitHub metadata before work.
- Run available repository validation and tests.
- Never let one failing benchmark terminate the whole command-center run.
- Record failures for later repair.
- Keep development on review branches rather than directly changing main.
- Keep secrets outside the repository.
- Prefer free/local/open tooling unless a paid model/service is explicitly approved.

## Development loop

`pull → inspect → benchmark → sandbox → repair → test → review → commit → push → GitHub Actions`

The command center is intentionally conservative: it can prepare and validate work, but it does not silently merge production changes, modify secrets, spend money, or contact external parties.
