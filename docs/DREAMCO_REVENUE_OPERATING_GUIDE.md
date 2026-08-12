# DreamCo Revenue Operating Guide

## Purpose

Define the revenue architecture for DreamCo's Money Operating System while separating measurable product revenue from projections and high-risk/regulated activities.

## Primary Streams

| Stream | Repository area | Operating model |
|---|---|---|
| Affiliate marketing | `money/affiliate_engine.js` | Tracked referral links and conversion attribution |
| Lead generation | `money/lead_seller.js` | Capture, qualification, buyer matching, sale attribution |
| Services/automation | `workflows/fiverr.json` | Proposal, fulfillment and follow-up automation |
| Real estate tooling | `workflows/real_estate.json` | Market research, deal analysis and lead workflows |
| Grants assistance | `workflows/grants.json` | Opportunity discovery, eligibility research and drafting support |
| Crypto analytics/trading | `workflows/crypto.json` | Research, simulation and risk-controlled execution where permitted |
| Legal-claims assistance | `workflows/legal_money.json` | Intake, organization and research support with appropriate professional review |

## Recommended Commercial Priority

1. SaaS subscriptions
2. Lead-generation products
3. Agency/automation services
4. Affiliate products
5. Bot marketplace
6. Real-estate analytics/tools
7. Grant opportunity assistance
8. Crypto analytics/paper trading

## Revenue Attribution Requirements

Every monetization workflow should record, where applicable:

- bot ID
- division
- workflow ID
- user/customer ID
- acquisition source
- campaign/referral identifier
- event timestamp
- transaction ID
- gross amount
- fees
- net amount
- currency
- status
- refund/chargeback state

## Lead Generation

Lead scoring can use completeness, source quality, category relevance, freshness and engagement. Scores are decision-support signals and must not be represented as guarantees of lead value.

Before selling a lead, enforce consent, privacy, applicable platform rules, buyer eligibility, duplicate detection and audit logging.

## Affiliate Marketing

Store affiliate program credentials only in approved secret stores/environment configuration. Generate tracked links through a central attribution layer and reconcile clicks/conversions against provider reports.

Do not fabricate commissions or conversion results.

## Services Marketplace

Automation should assist with discovery, proposal drafting, scheduling, fulfillment and follow-up. Platform rules and client agreements must be respected; bots must not misrepresent human identity or qualifications.

## Real Estate

Use public/authorized listing and market data. Licensing, agency relationships, advertising requirements, fair-housing obligations, local rules and professional review must be respected. AI-generated deal analysis is an aid, not a guarantee of investment performance.

## Grants

The system may discover opportunities, summarize eligibility, organize evidence and assist with drafts. It must not claim guaranteed awards, invent eligibility, fabricate certifications, or submit false information.

## Crypto

Default to simulation/paper trading. Enforce configurable exposure, stop-loss, take-profit, volatility and drawdown controls. No strategy should be represented as guaranteed profitable. Production execution requires explicit user authorization and appropriate exchange/security controls.

## Legal/Claims

Bots can assist with intake, document organization, public-information research and workflow administration. They should not impersonate attorneys, provide unauthorized legal representation, or guarantee claim outcomes.

## Dashboard Metrics

The Command Tower/revenue dashboard should expose actual measurements such as:

- total gross revenue
- net revenue
- transactions
- active revenue workflows
- revenue by bot/division
- leads generated
- qualified leads
- lead conversion rate
- customer acquisition cost when available
- subscription MRR/ARR when available
- refunds/chargebacks
- pipeline value separately from realized revenue

## Revenue Claims Policy

Planning estimates are targets, scenarios or market assumptions. They must be visually and semantically separated from realized revenue. Dashboards should never label an estimate as revenue.
