# Original Bot And Code Recovery

Recovery branch: `codex/recover-buddy-after-import`

Source branch used for recovery: `codex/bot-test-dashboard`

## Restored Scope

The original bot and code trees from the earlier DreamCo repository history were restored additively into this recovery branch. Current recovery work was preserved, including the 45-division JSON catalog in `App_bots/`, Buddy media fallbacks, safe deal rails, generated reports, config, and control tower systems.

## Restored Bot Inventory

- Bot-related files restored/preserved in primary bot folders: 7,080
- Python bot/source files: 5,658
- `bot_profile.json` files: 1,249
- Original app-category Python bots restored separately: 54

## Important Path Decision

The current branch uses `App_bots/` for the 45 division JSON catalog. The older repository used `App_bots/` for Python app-category bots such as `music_app_bot.py`.

To keep both systems, the old Python app-category bots were restored here:

`original-bots/app-category-python/App_bots/`

Example:

`original-bots/app-category-python/App_bots/music_app_bot.py`

## Restored Code Areas

Major restored areas include:

- `BuddyAI/`
- `Business_bots/`
- `Fiverr_bots/`
- `Marketing_bots/`
- `Occupational_bots/`
- `Real_Estate_bots/`
- `Side_Hustle_bots/`
- `DreamFinance/`
- `bots/`
- `python_bots/`
- `java_bots/`
- `backend/`
- `frontend/`
- `api/`
- `core/`
- `framework/`
- `integrations/`
- `marketplace/`
- `sandbox/`
- `registry/`
- `ontology/`
- `workflows/`

## Verification

- Python syntax compilation passed across restored bot trees.
- TypeScript check passed.
- Production build passed.
- Platform-name scrub scan passed after restoration.
