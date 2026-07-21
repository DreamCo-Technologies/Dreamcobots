# Bot Owner Settings Report

Treat every DreamCo bot, including high-risk or previously blocked bots, as a supervised business-owner bot with clear on/off controls, permissions, approval gates, and safe-mode guardrails.

## Summary

- Bots with owner settings: 1248 / 1248
- Business-owner enabled bots: 1248
- Business-manager enabled bots: 1248
- Autonomous money discovery enabled bots: 1248
- AI model council enabled bots: 1248
- Model training/eval enabled bots: 1248
- Safe-mode enabled bots: 1248
- High-risk bots: 1096
- High-risk bots unblocked for safe work: 1096
- Live-action approval required bots: 1248
- Settings controls ready: 15

## Guardrails

- Safe mode stays on by default for every bot.
- High-risk bots can work like other bots in sandbox and business-owner mode.
- Live actions require explicit owner approval and audit evidence.
- Settings toggles expose capability state but do not bypass approval gates.
- Every risky action must produce an approval packet before execution.
- Every bot acts as a supervised business manager for its category, not as an unsupervised money operator.
- Every bot may use model-council advice in sandbox mode, but live model routing, paid batches, training on customer data, and dataset sales require approval.
- All user, client, payment, people, and credential data stays governed by privacy and secret policies.

## Always Require Approval

- send_outreach
- submit_bid
- submit_grant_application
- publish_app_or_store_listing
- production_model_routing_change
- fine_tune_or_train_on_customer_data
- sell_or_publish_training_dataset
- paid_model_benchmark_batch
- buy_domain
- run_paid_ad
- collect_or_move_money
- place_trade_or_financial_order
- contact_candidate_or_customer
- make_hiring_or_rejection_decision
- provide_legal_medical_tax_financial_claim
- change_credentials
- mutate_third_party_account
- production_deploy
- delete_or_destroy_repository_data