# 5S Workplace Audit Tool

Audit tool based on the 5S workplace methodology: Sort, Set in Order, Shine, Standardize, Sustain.

## Tiers
- **Free** ($0/mo): Basic audit, 5S scoring
- **Pro** ($29/mo): Detailed reports, trend analysis
- **Enterprise** ($99/mo): Multi-location, custom templates

## Usage
```python
import sys
sys.path.insert(0, "automation-tools/workplace_audit_tool")
from workplace_audit_tool import WorkplaceAuditTool

tool = WorkplaceAuditTool(tier="pro")
result = tool.run_audit("warehouse", items)
```
