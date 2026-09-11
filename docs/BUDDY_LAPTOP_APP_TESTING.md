# Buddy Laptop App Testing

This repository can now run Buddy on this laptop with a safe local Elite test entitlement.

## Start The Full Local App

```bash
npm run buddy:laptop:app
```

If `npm` is not installed on this laptop shell, run the launcher directly with Node:

```bash
node tools/run_buddy_laptop_app.mjs
```

Open:

- `http://localhost:5000/buddy`
- `http://localhost:5000/pricing`
- `http://localhost:5000/api/stripe/subscription-status`

The laptop launcher binds to `127.0.0.1` by default so it is reachable from this computer without exposing the test server on the wider network.

Expected local subscription response:

```json
{
  "hasActiveSubscription": true,
  "tier": "elite",
  "source": "local_test_entitlement",
  "isTestEntitlement": true
}
```

This does not create, change, or prove a real Stripe payment. It only unlocks the highest tier locally so Buddy, pricing gates, dashboards, and bots can be tested.

If `DATABASE_URL` is missing, the launcher supplies a local placeholder so the frontend and local entitlement endpoint can boot. Full database-backed routes still require a real local Postgres database.

If `AI_INTEGRATIONS_OPENAI_API_KEY`, `OPENAI_API_KEY`, and `OPENAI_ADMIN_KEY` are all missing, the launcher supplies an invalid local placeholder so provider clients can initialize. Real model, image, audio, and agent calls still require a real approved API key.

## Start The GitHub Pages Preview

```bash
npm run buddy:laptop:pages
```

Open:

- `http://localhost:4173/buddy.html`

The Pages preview runs `tools/build_buddy_public_site.py --check` before serving the static site.

## Test Commands

```bash
npm run buddy:laptop:check
node --import tsx --test tests/local-test-entitlement.test.ts
```

## Safety Rules

- Production never honors `DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT`.
- Real Stripe still requires valid `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY`.
- GitHub Pages remains a static public surface; private Buddy backend actions run only through the local app or a separately approved backend deployment.
