# Stripe Builder Bot

Help Buddy build, test, and prepare Stripe revenue systems without exposing secrets or taking live payment actions without approval.

## Summary

- build_modules: 7
- required_env_vars: 8
- approval_gates: 8
- live_money_blocked_without_approval: True
- secret_values_stored_in_repo: False
- github_notifications_supported: True
- email_notifications_supported: True

## Build Modules

- **Offer Catalog Builder**: products, prices, tiers, trial rules, refund policy notes
- **Checkout Builder**: payment link drafts, checkout session config, success URL, cancel URL
- **Subscription Builder**: monthly plans, annual plans, upgrade paths, dunning notes
- **Webhook Builder**: event allowlist, signature verification checklist, retry plan, event ledger schema
- **Payment Notification Builder**: owner email alerts, GitHub issue alerts, dashboard payment feed, failure notices
- **Test Mode Builder**: test cards checklist, webhook fixture plan, refund test, subscription lifecycle test
- **Secret Setup Builder**: required env var list, Secret Manager map, GitHub Secret map, rotation checklist

## Approval Gates

- create_live_product_or_price
- publish_payment_link
- send_invoice
- accept_live_payment
- issue_refund
- change_payout_or_bank_settings
- email_customer
- create_github_payment_issue
