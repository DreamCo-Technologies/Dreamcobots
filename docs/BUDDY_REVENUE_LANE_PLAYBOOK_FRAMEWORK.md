# Revenue-lane playbook framework

This framework covers every lane in the canonical `money_os/config/revenue_lanes_expanded.json` catalog. It supplies a repeatable six-stage workflow for opportunity discovery, qualification, economics, offer/fulfillment design, approved experiments, and evidence-based measurement.

## What is included

- One record for every canonical revenue lane, with the lane's value proposition and monetization models.
- Shared task sequence and evidence outputs.
- Lane-specific safeguards for higher-risk areas such as procurement, insurance, tax incentives, real estate, franchise opportunities, AI model services, travel, licensing, unclaimed property, receipts, and resale.
- Explicit blocks on unapproved outreach, ad spend, bids, transfers, and bypassing credentials or anti-abuse controls.
- Mastery evidence requirements that include sandbox practice, holdout transfer, human review, regression, and delayed recall.

## What remains to be authored

The framework does **not** contain a complete detailed course for each lane. Each lane still needs current source research, step-by-step software instructions, worked examples, exercises, assessments, jurisdiction-specific reviews where relevant, and verified sandbox results. The `content_status` field intentionally remains `framework_only_not_a_completed_lane_course`.

## Validate

```bash
python -m pytest -q tests/test_buddy_revenue_lane_playbook_framework.py
```

Revenue forecasts and simulated experiments are not revenue. Financial results must be reconciled to verified payment-provider events. Live payment, spending, outreach, and contract actions remain controlled by existing approval gates.
