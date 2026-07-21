# Smart Meeting Scheduler

Intelligent meeting scheduler with conflict detection, timezone support, and calendar analytics.

## Tiers
- **Free** ($0/mo): 5 meetings/month, basic scheduling
- **Pro** ($24/mo): Unlimited meetings, timezone support, conflict detection, reminders
- **Enterprise** ($89/mo): Calendar sync, analytics, API access

## Usage
```python
import sys
sys.path.insert(0, "automation-tools/smart_meeting_scheduler")
from smart_meeting_scheduler import SmartMeetingScheduler

scheduler = SmartMeetingScheduler(tier="pro")
result = scheduler.schedule_meeting("Team Sync", "2025-01-15T10:00:00", 60, ["alice@co.com"])
```
