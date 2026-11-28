# Stage 08 — Media Studio

This stage provides the deterministic CPU-side shot planner.

- `director.py`: validates production requests, builds plans, and exposes a rights-gated render adapter contract.
- `shot-list.example.json`: minimal example input.
- `tests/test_media_director.py`: CPU-only unit tests.
- `docs/DREAMCO_MEDIA_FOUNDRY.md`: architecture and operating notes.

Run `python stages/08_media_studio/director.py stages/08_media_studio/shot-list.example.json --output media-plan.json`.

No GPU, model downloads, API keys, or external services are needed for planning.
