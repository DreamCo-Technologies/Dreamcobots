# DreamXXX Systems

Each folder here is a self-contained system generated from `App_bots/*.json`.

Run locally:

```bash
python3 tools/scan_bot_fleet.py --worklist reports/AUTONOMOUS_WORKLIST.md
python3 tools/build_dream_systems.py --mode all
python3 systems/DreamRealEstate/system_orchestrator.py
```
