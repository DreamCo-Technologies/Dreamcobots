# Production scan

Runtime release checks pass. This checkout is not production-certified.

Still required on the host, not in git:

- `DATABASE_URL`
- `STRIPE_WEBHOOK_SECRET`
- a Stripe secret key and publishable key
- an OpenAI key if those routes stay enabled
- `OWNER_BILLING_TOKEN` for billing restore and the customer portal

The portal no longer opens the first active subscription or an emailed customer. Restore and portal require the owner token.

GitHub Pages still needs the source switched to GitHub Actions before the Pages workflow can publish. Open Hugging Face and Pages pull requests were not merged from this scan.
