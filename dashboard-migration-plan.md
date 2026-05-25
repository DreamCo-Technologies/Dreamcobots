# Dashboard Migration Plan

## Recommended shortlist
- tests/test_web_dashboard.py (overall score: 88)
- ui/web_dashboard.py (overall score: 87)
- dashboard_inventory_builder.py (overall score: 75)
- dashboard_feature_extractor.py (overall score: 74)
- Business_bots/administrative_support_industry_bot.py (overall score: 70)
- Business_bots/public_administration_bot.py (overall score: 70)
- Occupational_bots/administrative_support_bot.py (overall score: 70)
- bots/ai-models-integration/data_analytics/data_analytics_bot.py (overall score: 64)
- dashboard_capability_adapter.py (overall score: 62)
- dashboard/static/dashboard.js (overall score: 56)

## Migration candidate inputs
- Candidates discovered: 70
- Dead dashboards: 2

## Consolidation direction
- Keep one governed dashboard framework with modular capability panels.
- Prioritize dashboards with high governance + automation + security scores.
- Deprioritize duplicated dashboards with penalties.
