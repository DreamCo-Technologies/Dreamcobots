# Shopify Automation Bot

A tier-aware AI-powered Shopify store automation bot for the Dreamcobots platform. Syncs inventory, processes orders with automated actions, and manages custom workflows based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.shopify_automation_bot.bot import ShopifyAutomationBot
from bots.shopify_automation_bot.tiers import get_shopify_automation_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)        | Pro ($49/mo)                             | Enterprise ($299/mo)                          |
|--------------------------|---------------------|------------------------------------------|-----------------------------------------------|
| Connected stores         | 1                   | 3                                        | Unlimited                                     |
| Orders per month         | 100                 | 10,000                                   | Unlimited                                     |
| Inventory sync           | Basic (10 items)    | Full (100 items)                         | Bulk (1,000 items)                            |
| Automated actions        | Confirmation only   | Confirmation + inventory + fulfillment   | Full suite + workflow + CRM                   |
| Custom workflows         | ❌                  | ✅                                       | ✅                                            |
| API access               | ❌                  | ❌                                       | ✅                                            |
| Bulk operations          | ❌                  | ❌                                       | ✅                                            |

## Usage

### Initialize the bot

```python
from bots.shopify_automation_bot.bot import ShopifyAutomationBot
from tiers import Tier

bot = ShopifyAutomationBot(tier=Tier.PRO)
```

### Sync inventory

```python
result = bot.sync_inventory("store_123")
print(result)
# {
#   "store_id": "store_123",
#   "synced_items": 100,
#   "status": "full_sync_complete",
#   "tier": "pro"
# }
```

### Process an order

```python
order = {
    "order_id": "ORDER-456",
    "items": [{"sku": "WIDGET-01", "quantity": 2}],
    "customer": {"id": "CUST-789", "email": "customer@example.com"}
}

result = bot.process_order(order)
print(result)
# {
#   "order_id": "ORDER-456",
#   "status": "processed",
#   "automated_actions": [
#     "send_confirmation",
#     "update_inventory",
#     "notify_fulfillment"
#   ],
#   "tier": "pro"
# }
```

### Automate a workflow (PRO/ENTERPRISE)

```python
workflow = {
    "name": "low_stock_reorder",
    "trigger": "inventory_below_threshold",
    "actions": ["send_po", "notify_manager"]
}

result = bot.automate_workflow(workflow)
print(result)
# {
#   "workflow_id": "uuid-...",
#   "name": "low_stock_reorder",
#   "status": "active",
#   "tier": "pro"
# }
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 5,
#   "requests_remaining": "995",
#   "stores_connected": 1,
#   "orders_processed": 3,
#   "buddy_integration": True
# }
```

## License

MIT
