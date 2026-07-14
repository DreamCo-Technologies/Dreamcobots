# Buddy Actions Operator

The Actions page can now operate Buddy through supervised prompt packets.

## What works

- Open Buddy Operator from the Actions page.
- Type a prompt for bot builds, Stripe fixes, Vibe Studio work, deployment planning, tests, APIs, webhooks, tools, workflows, or libraries.
- Submit the prompt to `/api/buddy-ops/prompt`.
- Receive a governed operation packet with builder type, sandbox mode, outputs, tests, approval gates, blocked live actions, branch hint, and next actions.
- See recent packets in the Actions page operation queue.
- Read the queue from `/api/buddy-ops`.

## Safety mode

Every packet starts as `sandbox_first_pull_request_review`.

Blocked until owner approval:

- external outreach
- money movement
- production deploys
- credential changes
- destructive file or git operations

## Next level

The next step is turning approved packets into automatic branch creation, test execution, and draft pull requests from the dashboard.
