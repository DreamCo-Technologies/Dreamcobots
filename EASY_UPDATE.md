# DreamCo Easy Update

You should not need to know coding to keep this repository working.

## The easy way

1. Open **GitHub**.
2. Open your DreamCo repository.
3. Tap **Actions**.
4. Tap **DreamCo Control Center**.
5. Tap **Run workflow**.
6. Pick what you want to check.
7. Tap the green **Run workflow** button.

Start with **check-everything**.

A green check means the selected checks passed. A red X means something needs fixing.

## If you see a red X

1. Open **Agents**.
2. Pick **Buddy Debugger**.
3. Say: **Fix the failed DreamCo Actions run.**

For a normal update, pick **Easy Updater** and say what you want in plain language, for example:

- Add a new bot for plumbers.
- Make Buddy better at finding grants.
- Add a music button.
- Check if my sales bots are in the right division.
- Fix whatever is broken.

The agent should find the right files, make the change, run the right tests, and explain the result.

## The seven simple checks

- **check-everything** — best first choice.
- **check-actions** — checks whether GitHub Actions files point to real scripts and supported action versions.
- **test-buddy** — checks Buddy's main systems.
- **test-resources** — checks the resource library and sandbox coverage.
- **test-fleet** — checks bots, divisions, placement, and fleet quality.
- **test-website** — checks the Buddy website build.
- **full-test** — runs the broad repository test suite.

## Rules for every DreamCo copy

A DreamCo-based repository should keep the same basic structure:

- `.github/workflows/` — buttons and automatic checks.
- `.github/agents/` — coding/debug helpers.
- `App_bots/` — canonical bot definitions.
- `config/` — policies, catalogs, and generated evidence.
- `shared/` — reusable contracts and shared systems.
- `tools/` — builders, audits, and generators.
- `tests/` — executable proof.
- `website/` — the Buddy public interface.

Do not make a second copy of a shared system when one already exists. Improve the shared owner instead.

## The most important rule

**Describe what you want. Let DreamCo find the code.**

Users should not have to learn file names, YAML, Git commands, package managers, or bot internals just to make a safe update.
