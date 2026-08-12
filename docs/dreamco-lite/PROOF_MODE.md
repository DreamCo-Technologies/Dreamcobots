# DreamCo Lite — Proof Mode

## Purpose

Proof Mode exists to prevent DreamCo from upgrading Money Bot before Money Bot v1 has demonstrated useful output in the real world.

Do not build Money Bot v2 simply because telemetry, embedded debugging, adaptive prompts, or self-improvement sound useful. First identify the actual problems exposed by v1.

## Required Test Scenarios

Run at least three materially different lead-generation scenarios. Example set:

1. Roofing companies in Wisconsin
2. Local gyms in Chicago
3. Real estate agents in Texas

Equivalent live scenarios may be substituted when they better match a real sales opportunity.

## Lead Quality Review

For each run, score:

- Are the leads real?
- Are they relevant to the requested niche/location?
- Is the business/contact data usable?
- Would a salesperson actually contact these leads?

Recommended score: 1–10.

## Message Quality Review

For each run, score:

- Does the message sound natural?
- Does it use the lead's actual context?
- Is the value proposition clear?
- Would the message be sent with little or no editing?
- Does it avoid unsupported claims or fabricated personalization?

Recommended score: 1–10.

## Action Test

The most important test is whether the output can be acted on.

For at least one lead in each scenario:

1. review the contact information;
2. review the generated outreach;
3. edit only if necessary;
4. determine whether the message is ready to send or use in a real sales interaction.

Where appropriate and authorized, use the output in an actual outreach attempt and record the result.

## Manual Scorecard

No complex telemetry platform is required for Proof Mode. A simple record is enough.

```text
Scenario:
Niche:
Location:
Lead source:

Lead quality: __/10
Message quality: __/10
Actionability: __/10

Problems observed:
- 
- 

What worked:
- 
- 

Would I use this again? yes/no
Would I pay for this output? yes/no/unclear
```

## Proof Gate

Money Bot v1 passes Proof Mode when:

- multiple runs return operationally useful leads;
- outreach is usable with limited editing;
- at least one real user can complete the workflow without developer intervention;
- observed failures are specific enough to define the v2 backlog.

If those conditions are not met, improve v1 instead of expanding the architecture.

## What Proof Mode Produces

The result of Proof Mode is not merely a pass/fail decision. It becomes the evidence-based Money Bot v2 specification.

Examples:

- If lead quality is weak, improve sourcing/ranking before adding telemetry.
- If messages are generic, improve prompt/context construction before adding autonomous builders.
- If lead sources fail frequently, add targeted retry/fallback logic based on those real failures.
- If users struggle with the UI, fix the interaction before building a visual workflow builder.

**v1 discovers the problems. v2 solves the problems that actually occurred.**
