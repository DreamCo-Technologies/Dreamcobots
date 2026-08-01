# Deployment Cost Policy

DreamCo's default public release is a static prototype with a target hosting cost of $0 per month.

## Default Release

- Publish only `website/`.
- Do not install application dependencies during hosting builds.
- Do not deploy API routes, serverless functions, cron jobs, databases, media renderers, or model inference with the static release.
- Deploy deliberately after local checks instead of creating a provider build for every branch push.
- Keep generated GitHub artifacts for one day.
- Keep authentication, payments, private data, and provider credentials outside the static site.

Run the cost preflight before a release:

```bash
python3 tools/check_deployment_cost_policy.py
python3 tools/build_buddy_public_site.py --check
```

## Provider Boundaries

The static prototype can use a provider's free plan only while that use complies with the provider's current terms. Vercel Hobby is limited to personal, non-commercial use. GitHub Pages is not intended to operate an online business, ecommerce site, or commercial SaaS. Before DreamCo sells access, use a plan or host whose terms permit the intended commercial activity.

Dynamic Buddy capabilities should run locally first. Any external database, API, rendering engine, model, messaging service, payment service, or scheduled worker must show its expected cost and require the owner's explicit approval before activation.
