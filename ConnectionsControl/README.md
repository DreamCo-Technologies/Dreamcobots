# ConnectionsControl

> **GLOBAL AI SOURCES FLOW** — Unified multi-platform control layer for the DreamCobots ecosystem.

ConnectionsControl is the central nervous system of DreamCobots. It aggregates every communication channel, alert pathway, and emergency control into a single, coherent package — so operators can monitor, command, and shut down the entire bot fleet from any surface: mobile PWA, TV dashboard, REST API, Telegram, Slack, Discord, SMS, Zoom, or a gaming console browser.

---

## Directory Structure

```
ConnectionsControl/
├── __init__.py               # Package entry-point
├── control_panel.py          # Unified ControlPanel class
├── kill_switch.py            # Global emergency stop
├── telegram_integration.py   # Telegram bot commands & alerts
├── slack_integration.py      # Slack alerts & workflow triggers
├── discord_integration.py    # Discord server messaging & roles
├── sms_kill_switch.py        # SMS-triggered kill switch (Twilio-style)
├── webhook_manager.py        # Webhook registry & event dispatcher
├── rest_api.py               # REST endpoint registry & simulator
├── zoom_bot.py               # Zoom meeting scheduler & reporter
├── roku_dashboard.py         # Roku TV KPI display
├── gaming_integration.py     # Xbox / PlayStation / Switch browser dashboard
└── mobile_pwa/
    └── index.html            # Progressive Web App control panel
```

---

## Platform Integrations

### 1. Kill Switch (`kill_switch.py`)

The `KillSwitch` class provides a global emergency stop for every registered bot and service.

| Method | Description |
|---|---|
| `activate(reason)` | Activates kill switch, halts all registered bots, logs the event |
| `deactivate()` | Restores normal operations |
| `register_bot(bot_id, callback)` | Register a bot stop-callback |
| `halt_all_bots()` | Calls every registered stop-callback |
| `get_log()` | Returns full activation history |

**Usage:**
```python
from ConnectionsControl import KillSwitch

ks = KillSwitch()
ks.register_bot("sales_bot", lambda: sales_bot.stop())
ks.activate("Suspicious activity detected.")
```

---

### 2. Telegram Integration (`telegram_integration.py`)

Send messages and handle slash commands via a Telegram bot.

**Supported commands:** `/status`, `/stop`, `/start`, `/dashboard`, `/alerts`

```python
from ConnectionsControl.telegram_integration import TelegramIntegration

tg = TelegramIntegration()
tg.configure(bot_token="YOUR_TOKEN", chat_id="YOUR_CHAT_ID")
tg.send_message("🚨 Critical alert: revenue drop detected.")
response = tg.handle_command("/status")
```

---

### 3. Slack Integration (`slack_integration.py`)

Send severity-tagged alerts and trigger Slack workflows.

```python
from ConnectionsControl.slack_integration import SlackIntegration

slack = SlackIntegration()
slack.configure(api_token="xoxb-...", default_channel="#ops-alerts")
slack.send_alert("#ops-alerts", "Bot cluster offline.", severity="critical")
slack.trigger_workflow("escalate_incident", {"bot": "sales_bot"})
```

---

### 4. Discord Integration (`discord_integration.py`)

Post messages to Discord channels and assign roles to users.

**Supported commands:** `!status`, `!alert <level>`, `!report`

```python
from ConnectionsControl.discord_integration import DiscordIntegration

discord = DiscordIntegration()
discord.configure(bot_token="YOUR_TOKEN", guild_id="YOUR_GUILD")
discord.send_message("#general", "DreamCobots systems nominal.")
discord.assign_role(user_id="123456", role="Operator")
```

---

### 5. SMS Kill Switch (`sms_kill_switch.py`)

SMS-triggered emergency stop with Twilio-compatible interface. Operators can text `STOP`, `KILL`, `HALT`, or `EMERGENCY` to activate, and `START`, `RESTORE`, or `RESUME` to deactivate.

```python
from ConnectionsControl.sms_kill_switch import SMSKillSwitch

sms = SMSKillSwitch()
sms.configure(
    account_sid="AC...",
    auth_token="...",
    from_number="+15550001234",
    to_numbers=["+15559990000", "+15558880000"],
)
sms.trigger_kill_switch()                        # broadcasts alert SMS
sms.handle_incoming_sms("+15559990000", "STOP")  # activates kill switch
```

---

### 6. Webhook Manager (`webhook_manager.py`)

Register webhook endpoints and dispatch signed events.

```python
from ConnectionsControl.webhook_manager import WebhookManager

wm = WebhookManager()
wm.register_webhook(
    name="ops_hook",
    url="https://example.com/hook",
    events=["alert", "kill_switch"],
    secret="s3cr3t",
)
wm.trigger_event("alert", {"message": "High CPU detected.", "severity": "warning"})
```

Payloads are signed with HMAC-SHA256 when a `secret` is provided.

---

### 7. REST API Manager (`rest_api.py`)

Register and simulate REST API endpoints; auto-generate Markdown documentation.

```python
from ConnectionsControl.rest_api import RestAPIManager

api = RestAPIManager()
api.register_endpoint(
    path="/api/status",
    method="GET",
    handler=lambda _: {"status": "ok"},
    description="Health check endpoint.",
    auth_required=False,
)
response = api.simulate_request("/api/status", "GET")
print(api.generate_api_docs())
```

---

### 8. Zoom Bot (`zoom_bot.py`)

Schedule Zoom meetings and attach automated reports.

```python
from ConnectionsControl.zoom_bot import ZoomBot
from datetime import datetime

zoom = ZoomBot()
zoom.configure(api_key="KEY", api_secret="SECRET")
meeting = zoom.schedule_meeting("Weekly Ops Review", datetime(2025, 1, 20, 9, 0), 60)
zoom.send_report_to_meeting(meeting.meeting_id, "Revenue up 12%. All bots nominal.")
zoom.start_meeting(meeting.meeting_id)
zoom.end_meeting(meeting.meeting_id)
```

---

### 9. Roku Dashboard (`roku_dashboard.py`)

Push live KPI data to a Roku TV for executive monitoring.

```python
from ConnectionsControl.roku_dashboard import RokuDashboard, KPIMetrics

roku = RokuDashboard()
roku.configure(device_ip="192.168.1.50")
metrics = KPIMetrics(revenue=128500.00, active_bots=12, alerts=2, throughput=847.0, uptime=99.9)
roku.push_dashboard(metrics)
```

The rendered screen uses box-drawing characters for a clean TV display.

---

### 10. Gaming Integration (`gaming_integration.py`)

Access the DreamCobots dashboard from Xbox, PlayStation, or Nintendo Switch browsers.

```python
from ConnectionsControl.gaming_integration import GamingIntegration, ConsoleType

gaming = GamingIntegration()
gaming.configure(ConsoleType.XBOX)
url = gaming.generate_dashboard_url()
html = gaming.render_console_view({"revenue": 128500, "active_bots": 12, "alerts": 2, "uptime": 99.9})
```

Supported consoles: `xbox`, `playstation`, `switch`, `generic`.

---

## Unified Control Panel (`control_panel.py`)

`ControlPanel` is the single entry-point for all integrations. It exposes:

| Method | Description |
|---|---|
| `broadcast_alert(message, severity)` | Send alert to all active platforms simultaneously |
| `activate_kill_switch(reason)` | Activate kill switch + broadcast critical alert |
| `deactivate_kill_switch()` | Deactivate kill switch + broadcast info alert |
| `get_platform_status()` | Dict of status for every registered platform |
| `get_control_matrix()` | Formatted ASCII table of platform connectivity |
| `ping_all_platforms()` | Update last-ping timestamps for all platforms |
| `register_platform(name, integration)` | Add a custom platform integration |

```python
from ConnectionsControl import ControlPanel

panel = ControlPanel()

# Configure individual integrations as needed
panel._telegram.configure("TOKEN", "CHAT_ID")
panel._slack.configure("xoxb-...", "#alerts")

# Broadcast to all configured platforms
panel.broadcast_alert("Maintenance window starting in 5 minutes.", severity="warning")

# Emergency stop
panel.activate_kill_switch("Unauthorized access detected.")

# View platform matrix
print(panel.get_control_matrix())
```

---

## Mobile PWA (`mobile_pwa/index.html`)

A Progressive Web App control panel optimised for mobile screens. Features:

- **KPI cards** — Active Bots, Alerts, Throughput, Uptime
- **Platform status indicators** — live green/grey dots per integration
- **Kill Switch button** — toggles between ACTIVATE and DEACTIVATE states
- **Dark theme** with CSS custom properties for easy reskinning
- Auto-updating timestamp every 30 seconds

To install as a PWA, serve `mobile_pwa/` over HTTPS and add a `manifest.json` alongside `index.html`.

---

## Kill Switch — Quick Reference

| Trigger method | Command / Call |
|---|---|
| Python API | `ControlPanel().activate_kill_switch("reason")` |
| Telegram | `/stop` |
| Discord | `!alert critical` |
| SMS | Text `STOP` to the configured number |
| Mobile PWA | Tap **🚨 ACTIVATE KILL SWITCH** |

---

## Setup

1. Install the package (no external dependencies required for mock mode):
   ```bash
   pip install -e .
   ```

2. Import and configure:
   ```python
   from ConnectionsControl import ControlPanel
   panel = ControlPanel()
   ```

3. Configure each platform integration with its credentials before use (see individual sections above).

4. For production deployments, replace mock implementations with real SDK calls inside each integration class.

---

*GLOBAL AI SOURCES FLOW — DreamCobots ConnectionsControl*
