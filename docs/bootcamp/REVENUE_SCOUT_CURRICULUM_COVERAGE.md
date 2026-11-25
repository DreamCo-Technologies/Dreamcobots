# Revenue Scout curriculum coverage audit

DreamCo already has a Master Scout taxonomy, opportunity source categories, and revenue lanes. Those structures describe what the system intends to cover; they are not task-by-task lessons.

This audit measures each scout against eight required learning modules:

1. Discover opportunities and identify the user's actual objective
2. Verify the source, freshness, authority, eligibility caveats and provenance
3. Calculate economics, fees, taxes, time, costs and downside scenarios
4. Assess user fit, prerequisites, jurisdiction and alternatives
5. Identify scams, privacy, licensing, rights and terms-of-service risks
6. Prepare a practical checklist, comparison, draft or application packet
7. Require the right human approval before outreach, submission, purchase or commitment
8. Record verified outcomes, failures and reusable lessons

A module is ready for study review only when the artifact manifest points to an existing repository guide and records exercises, an assessment, citations, rights review and human review.

## Run

```bash
python -m pytest -q tests/test_revenue_scout_curriculum.py
python tools/audit_revenue_scout_curriculum.py
```

The audit deliberately reports curriculum gaps rather than generating fictional guides or inferring mastery. Opportunity discovery is not proof of a job, grant, contract, sale, investment return or successful transaction. The scout program's existing approval, privacy, licensing and anti-fraud guardrails remain in force.
