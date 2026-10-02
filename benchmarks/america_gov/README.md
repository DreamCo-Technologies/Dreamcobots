# America.gov sandbox

Sandboxed catalog of the America.gov front door and the government tasks it advertises.

Phase 1, launched September 29, 2026, only returns official guidance. Phase 2 transactions are 2027 previews. This runner never submits a form, enrollment, or payment.

```bash
python3 benchmarks/america_gov/sandbox.py
python3 benchmarks/america_gov/sandbox.py --list
python3 benchmarks/america_gov/sandbox.py --ask enroll_medicare --query "enroll me"
python3 -m unittest benchmarks.america_gov.test_sandbox
```

IRS tax filing, Department of War services, and Intelligence Community services are excluded, matching the September 29, 2026 executive order. Social Security numbers are blocked before a task runs.
