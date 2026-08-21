# Buddy Repair Intelligence Scorecard

The repair system is only considered to be getting smarter when measurable outcomes improve.

## Core metrics

### Diagnosis accuracy
How often Buddy's leading root-cause hypothesis matches the verified root cause.

### Repair success rate
Percentage of repairs that pass the original failing gate without regression.

### Regression rate
Percentage of repairs that create a new failure in affected or dependent systems.

### Time to verified repair
Elapsed time from canonical incident creation to verified resolution.

### Unnecessary action rate
Percentage of diagnostic/repair actions that produced little or no useful information.

### Cost per successful repair
Compute/tool/model cost divided by verified successful repairs.

### Confidence calibration
When Buddy reports high confidence, outcomes should actually be highly reliable. Overconfidence is treated as a defect.

### Transfer success
How often a previously learned repair strategy works on a genuinely similar new incident after prerequisite checks.

### Recurrence rate
How often the same root cause returns after a repair.

### Escalation quality
Human/Council escalations should occur when risk or uncertainty warrants them—not simply because Buddy is stuck.

## Intelligence progression

### Level 0 — Reactive
Detects failures and reports them.

### Level 1 — Guided repair
Can reproduce known failures and execute bounded repair playbooks.

### Level 2 — Diagnostic reasoning
Generates competing hypotheses and chooses informative tests.

### Level 3 — Transfer
Recognizes related failures and safely reuses validated strategies.

### Level 4 — System reasoning
Understands cross-repository dependencies, blast radius and second-order effects.

### Level 5 — Adaptive engineering
Improves its repair strategies based on measured outcomes while preserving safety gates and human control.

These are engineering capability levels, **not claims that Buddy is AGI**.

## Promotion rules

Buddy must not advance a repair strategy merely because one run succeeded.

Promotion requires, as appropriate:

- repeated successful applications;
- regression evidence;
- confidence calibration;
- no unacceptable security behavior;
- bounded cost;
- documented prerequisites;
- provenance back to source incidents.

## Dashboard recommendation

Show both current value and trend:

```text
Diagnosis accuracy       82%  ↑
Repair success           76%  ↑
Regression rate           4%  ↓
Time to verified repair  18m  ↓
Unnecessary actions       9%  ↓
Cost / repair            $X   ↓
Transfer success         61%  ↑
Recurrence                7%  ↓
Escalation quality       91%  ↑
```

Values above are examples only. The dashboard must use measured repository evidence and never invent metrics.

## Intelligence gate

A strategy is considered **learning-positive** only when it improves one or more target metrics without unacceptable regression in safety, reliability, cost or user impact.

The goal is not maximum autonomy. The goal is **increasingly capable, measurable, explainable and safe problem solving**.
