# Revenue and workforce task-playbook authoring queue

Run:

```bash
python tools/build_buddy_revenue_playbook_queue.py
pytest -q tests/test_buddy_revenue_playbook_queue.py
```

The builder expands the canonical 12 workforce/entrepreneurship training paths into one explicit authoring work item for each listed subject. It carries forward the existing 18-section task-playbook contract and adds verification gates for facts, eligibility, permissions, costs, human approvals, and independent acceptance tests.

Every item remains `not_authored`. The queue does not fabricate a completed playbook, current vendor pricing, licensing advice, job or grant eligibility, guaranteed income, or permission to contact third parties or spend money. Future work should replace each queue item with an original, reviewed playbook and link evidence before changing its status.
