# O*NET task-guide readiness audit

The O*NET curriculum builder already creates an occupation path and a per-task authoring brief. A brief is not a finished lesson. This audit measures the missing artifact work explicitly.

## Run

```bash
python -m pytest -q tests/test_onet_task_guide_readiness.py
python tools/audit_onet_task_guide_readiness.py --input path/to/onet-task-curricula.json --output onet-guide-readiness.json
```

A task is ready for human study review only when the curriculum records:
- a versioned authored guide with a repository content path;
- practice exercises and an assessment;
- source citations with URLs and access dates;
- an approved rights review; and
- an approved human review.

The audit reports counts by gap type and occupation. It does not generate fictional guide content, infer that an authoring brief is a guide, certify a learner, or mark Buddy as competent. A passing readiness report is not mastery evidence.
