# Buddy Merchant Value + Revenue Model

## Goal
Buddy should create measurable economic value for store owners and allow DreamCo to earn transparently from that value.

The priority is **merchant value first**: a revenue stream that makes the merchant worse off is not a successful Buddy outcome.

## Core loop

`Merchant consent → transaction/expense analysis → compare authorized offers → verify savings → merchant approval → implementation → measure actual savings → transparent revenue share`

## Ways Buddy can create merchant value

- identify lower-cost payment/processing options
- detect duplicate or unnecessary software spend
- optimize subscriptions and recurring expenses
- improve checkout conversion
- reduce failed-payment/retry losses
- improve inventory/reorder decisions
- identify better-qualified marketing/affiliate offers
- automate routine back-office work
- compare vendor/partner pricing

Savings must be measured against a defined baseline. Estimates are not counted as realized savings.

## DreamCo monetization

Possible monetization events include:

1. subscription/SaaS fee for Buddy
2. merchant-approved referral/affiliate commission
3. transaction/service fee where legally and contractually permitted
4. revenue share based on verified savings
5. marketplace/partner commission
6. premium automation services

The implementation should prefer transparent pricing and avoid hidden markups.

## Savings-share example

If Buddy verifies $1,000 of monthly savings and the merchant agreement specifies a 10% savings share:

- verified savings: $1,000
- DreamCo share: $100
- merchant retained savings: $900

The percentage is configurable and must be explicitly agreed to. The code clamps the share to a bounded range and never moves money itself.

## Transaction ledger

Every monetized event should retain, where applicable:

- merchant ID
- transaction ID
- gross amount
- fees
- net amount
- currency
- timestamp
- acquisition/referral attribution
- offer/vendor/processor identifier
- baseline
- measured savings
- DreamCo fee/share
- merchant retained value
- refund/chargeback status
- consent/agreement reference

## Guardrails

Buddy must not:

- secretly enroll merchants
- switch processors without authorization
- fabricate savings
- label projections as realized savings
- hide commissions
- expose payment credentials
- store raw payment-card data when a tokenized provider flow can be used
- promise a merchant that a particular option will always be cheapest

Payment movement remains delegated to approved payment providers and explicit merchant authorization.

## Metrics for the Actions/Prospectus system

Track separately:

- merchants served
- transactions analyzed
- verified savings
- merchant retained savings
- DreamCo revenue
- effective merchant ROI
- refund/chargeback rate
- churn
- average time to savings
- cost to serve
- revenue per merchant
- savings per transaction

This allows investors and operators to distinguish **merchant value created** from **DreamCo revenue generated**.
