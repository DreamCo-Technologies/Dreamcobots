# Universal library candidate verification queue

DreamCo currently has a partial seed inventory of software/library names and a canonical set of registry ecosystems. A seed name is not a verified package, supported version, safe dependency, documented API or licensed learning source.

This builder converts every candidate into a review queue with eight explicit tasks:
1. verify upstream identity;
2. map it to a canonical ecosystem/registry;
3. verify release/version and maintenance;
4. locate official docs/API references;
5. review license and training permissions;
6. review security and supply-chain signals;
7. design an isolated evaluation sandbox; and
8. author an original guide and benchmark.

## Run

```bash
python -m pytest -q tests/test_library_candidate_verification_queue.py
python tools/build_library_candidate_verification_queue.py
```

The generated queue is an artifact and is not committed as a 531-row snapshot. It keeps candidate records unverified, download blocked, execution prohibited, and training unauthorized until item-level evidence and human review exist. The ecosystem list is extensible and does not claim worldwide completeness.
