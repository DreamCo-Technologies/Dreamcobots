# Contributing to DreamCo

DreamCo should be easy to improve without knowing the whole repository.

## The simple path

1. Describe the change in plain language.
2. Use **Easy Updater** or make the smallest focused change yourself.
3. Reuse the canonical shared owner instead of duplicating systems.
4. Run the focused test.
5. Run `npm run easy:check` for normal changes, `npm run easy:fleet` for bot/division changes, or `npm run easy:resources` for resource/scout changes.
6. Open a pull request when review is appropriate.
7. Do not merge while required checks are red.

## Rules

- Do not weaken or delete meaningful tests to make CI green.
- Do not call a configuration or catalog entry a working runtime capability without executable evidence.
- Keep consequential external actions behind approval gates.
- Prefer shared infrastructure improvements over copying the same fix into many bots.
- Add regression coverage when fixing a real bug.
- Keep generated files generated; fix their canonical source or generator.

## If Actions fails

Open the failed run, then use **Agents → Buddy Debugger**. Give it the run URL and ask it to fix the first root cause and rerun the affected suite.
