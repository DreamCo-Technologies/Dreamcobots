# Stripe Builder Bot

Help Buddy build, test, and prepare Stripe revenue systems without exposing secrets or taking live payment actions without approval.

## Summary

- build_modules: 9
- required_env_vars: 8
- approval_gates: 10
- live_money_blocked_without_approval: True
- secret_values_stored_in_repo: False
- github_notifications_supported: True
- email_notifications_supported: True
- future_stripe_profiles_supported: True
- secret_rotation_supported: True
- secret_aliases_supported: 3

## Build Modules

- **Offer Catalog Builder**: products, prices, tiers, trial rules, refund policy notes
- **Checkout Builder**: payment link drafts, checkout session config, success URL, cancel URL
- **Subscription Builder**: monthly plans, annual plans, upgrade paths, dunning notes
- **Webhook Builder**: event allowlist, signature verification checklist, retry plan, event ledger schema
- **Payment Notification Builder**: owner email alerts, GitHub issue alerts, dashboard payment feed, failure notices
- **Test Mode Builder**: test cards checklist, webhook fixture plan, refund test, subscription lifecycle test
- **Secret Setup Builder**: required env var list, Secret Manager map, GitHub Secret map, rotation checklist
- **Stripe Profile Manager**: default Stripe profile, future account profiles, secret aliases, profile switch checklist
- **Secret Rotation Builder**: new secret plan, old secret retirement plan, dry-run validation, rollback checklist

## Secret Aliases

- stripe_secret_key: STRIPE_SECRET_KEY, STRIPE_API_KEY
- stripe_publishable_key: STRIPE_PUBLISHABLE_KEY
- stripe_webhook_secret: STRIPE_WEBHOOK_SECRET

## Future Stripe Account Workflow

- Create a new Stripe account or project in Stripe.
- Add profile-specific GitHub Secrets or Google Secret Manager entries.
- Run Stripe Secret Readiness in DRY_RUN mode.
- Run Stripe price audit to confirm every repository price still maps to a draft offer.
- Run Stripe revenue rescue to confirm webhook, email, and GitHub notification readiness.
- Approve profile switch only after a test checkout and webhook replay pass.
- Keep the old profile available until subscriptions, refunds, disputes, and reports are reconciled.

## Approval Gates

- create_live_product_or_price
- publish_payment_link
- send_invoice
- accept_live_payment
- issue_refund
- change_payout_or_bank_settings
- email_customer
- create_github_payment_issue
- add_or_rotate_stripe_secret
- switch_active_stripe_profile
