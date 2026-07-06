# DreamCo Sales Rep Bot Team

Goal: build a bot team that helps DreamCo find real customers, validate offers, create pricing, run ethical outreach, track KPIs, and improve daily.

This system does not promise money. It creates a disciplined sales machine so each bot has a job, proof, and measurable output.

## Sales operating loop

1. Define the problem.
2. Identify the customer.
3. Create the solution.
4. Build only the MVP bot system.
5. Validate with a real customer.
6. Create pricing.
7. Build a repeatable sales process.
8. Measure KPIs.
9. Review daily.
10. Continuously improve the system.

## Sales rep bot roles

| Bot | Mission | Output | KPI |
| --- | --- | --- | --- |
| Problem Finder Bot | Find painful, specific customer problems | Problem brief | problems validated/week |
| Customer Segment Bot | Identify reachable customer groups | Segment scorecard | qualified segments/week |
| Lead Research Bot | Find public, compliant lead data | Lead list with sources | qualified leads/day |
| Offer Builder Bot | Turn solution into a clear offer | Offer page/spec | offers launched/week |
| MVP Scope Bot | Keep builds small and shippable | MVP checklist | build time, scope creep |
| Validation Bot | Collect real customer feedback | Validation notes | interviews, yes/no decisions |
| Pricing Bot | Create simple pricing tests | Price ladder | conversion and margin |
| Outreach Writer Bot | Draft personalized outreach | Email/DM/call scripts | reply rate |
| Follow-Up Bot | Create follow-up sequences | Follow-up schedule | follow-up completion |
| CRM Logger Bot | Keep lead/customer records clean | CRM updates | data completeness |
| Objection Handler Bot | Track objections and best replies | Objection library | objection resolution rate |
| Demo Bot | Prepare demos and walkthroughs | Demo script | demos booked |
| Close Bot | Prepare close plan and payment link | Close checklist | close rate |
| Stripe Recovery Bot | Watch failed payments and invoices | Recovery tasks | recovered revenue |
| KPI Review Bot | Review daily metrics | Daily KPI report | daily review completed |

## Web research policy

Bots may search the web for public business data and client research only when:

- Sources are public and allowed.
- The bot stores source URLs.
- The bot does not collect private personal data unnecessarily.
- The bot does not spam.
- A human approves outbound outreach.

## Lead qualification score

Each lead gets a 0-100 score:

| Factor | Points |
| --- | ---: |
| Clear problem match | 25 |
| Budget likelihood | 20 |
| Reachable decision maker | 15 |
| Urgency signal | 15 |
| Fit with DreamCo offer | 15 |
| Source confidence | 10 |

## Required lead record

```json
{
  "leadId": "lead_001",
  "company": "Example Co",
  "segment": "local service business",
  "problem": "slow follow-up after web inquiries",
  "sourceUrls": ["https://example.com"],
  "score": 82,
  "recommendedOfferId": "dreamco-starter-audit",
  "assignedBot": "lead_research_bot",
  "status": "needs_human_review",
  "nextAction": "approve outreach draft"
}
```

## Outreach rules

- Never claim a bot did work it did not do.
- Never guarantee income or results.
- Use short, specific, honest messages.
- Tie every message to a real observed problem.
- Include one clear next step.
- Log every send, reply, objection, and outcome.

## Dashboard placement

Put these in **Dashboard**:

- Lead count.
- Qualified leads.
- Outreach drafted/sent.
- Replies.
- Booked calls.
- Offers created.
- Payment links created.
- Revenue by bot.
- Failed payments.
- Daily KPI review.

Put these in **Command Center**:

- Bot modes.
- Tool toggles.
- Web research permissions.
- GitHub Actions command runs.
- PRs and issue tasks.
- Missing file repairs.
- Model routing.
- Human approval queue.

## Daily sales review

Every day, the sales team should answer:

1. What customer problem did we validate today?
2. Which lead segment showed the strongest buying signal?
3. Which offer got the most interest?
4. Which outreach message got replies?
5. Which bot created revenue or moved a deal forward?
6. Which Stripe failures need recovery?
7. What should be improved tomorrow?
