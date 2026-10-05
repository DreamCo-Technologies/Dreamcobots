# America.gov sandbox

Sandboxed catalog of the America.gov front door and the government tasks it advertises.

Phase 1, launched September 29, 2026, only returns official guidance. Phase 2 transactions are 2027 previews. This runner never submits a form, enrollment, or payment.

```bash
python3 benchmarks/america_gov/sandbox.py
python3 benchmarks/america_gov/sandbox.py --list
python3 benchmarks/america_gov/sandbox.py --ask enroll_medicare --query "enroll me"
python3 -m unittest benchmarks.america_gov.test_sandbox
```

The large official source list is `massive_resources.json`. America.gov can supply cited how-to answers for DreamCo, but it has no public API and cannot file yet.
