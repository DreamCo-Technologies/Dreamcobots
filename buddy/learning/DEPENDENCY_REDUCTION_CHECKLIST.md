# Buddy Dependency-Reduction Checklist

Use this checklist for every capability cohort before reducing external routing.

- [ ] Comparable benchmark cohort identified
- [ ] Baseline native pass rate recorded
- [ ] Baseline external-assistance rate recorded
- [ ] At least three independent native passes recorded
- [ ] Holdout benchmark passed
- [ ] Regression suite passed
- [ ] No unresolved repeated failure signature
- [ ] Native result is reproducible
- [ ] External fallback remains available during transition
- [ ] Routing change is evidence-backed
- [ ] Post-routing cohort is monitored for regression

A capability must not be considered independent merely because external calls decreased. The quality gate is native performance plus validation evidence.
