# Buddy Beginner UI Quality Checklist

Use this checklist for every new page, button, action, workflow and dashboard.

## Before release

- [ ] Page has a plain-English title
- [ ] One-sentence explanation appears near the top
- [ ] Primary action is visually obvious
- [ ] Button says what will happen (`Run health check`, not `Execute`)
- [ ] Dangerous actions are clearly labeled
- [ ] Status is understandable without reading logs
- [ ] Errors include a plain-English explanation
- [ ] A safe fix is offered when one exists
- [ ] Retry is available for transient failures
- [ ] Learn/Teach Me explanation is available
- [ ] Advanced technical details are collapsible
- [ ] Mobile/touch layout works
- [ ] Keyboard navigation works
- [ ] Loading state is visible
- [ ] Empty state explains what to do next
- [ ] Success state explains what changed
- [ ] Permission requests explain why access is needed
- [ ] No fake success, fake data, or fake completion indicators
- [ ] User can see history/audit information when relevant
- [ ] User can cancel or undo where technically possible

## Beginner language

Prefer:

- `Check my project` over `Run diagnostics`
- `Fix this problem` over `Apply remediation`
- `Save a checkpoint` over `Commit`
- `Propose this change` over `Open PR`
- `Install Buddy` over `Deploy client`
- `Connect my device` over `Register endpoint`

Technical terminology may appear underneath for advanced users.

## Quality gate

A new feature should fail review if a first-time user cannot reasonably understand what the primary button will do.
