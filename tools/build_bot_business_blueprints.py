#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / 'App_bots'
STANDARD = json.loads((ROOT / 'config/bot-blueprint-standard.json').read_text(encoding='utf-8'))
REVENUE = json.loads((ROOT / 'config/dreamco-revenue-os.json').read_text(encoding='utf-8'))
OUT = ROOT / 'config/generated/bot-business-blueprints.json'
REPORT = ROOT / 'reports/BOT_BUSINESS_BLUEPRINTS.md'


def read_json(path, fallback):
    try: return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback
    except Exception: return fallback


def main() -> int:
    rows = []
    seen = set()
    for path in sorted(APP_BOTS.glob('*.json')) if APP_BOTS.exists() else []:
        doc = read_json(path, {})
        division = doc.get('division') or path.stem
        for bot in doc.get('bots', []):
            if not isinstance(bot, dict): continue
            slug = str(bot.get('slug') or '').strip()
            if not slug or slug in seen: continue
            seen.add(slug)
            caps = [str(x) for x in (bot.get('capabilities') or []) if str(x).strip()]
            target = bot.get('targetUsers') or 'target customer requires validation'
            description = bot.get('description') or ''
            rows.append({
                'slug': slug,
                'display_name': bot.get('displayName') or slug,
                'division': division,
                'source': str(path.relative_to(ROOT)),
                'blueprint_status': 'generated_requires_runtime_and_market_validation',
                'mission': description or f'Use verified {slug} capabilities to solve customer problems.',
                'job_description': description or f'Specialist worker for {slug}.',
                'target_customers': target,
                'industries_served': bot.get('industries') or ['derive from capability and market benchmark'],
                'problems_solved': [f'Customer problem related to {c}' for c in caps[:10]] if caps else ['requires capability validation'],
                'verified_features': caps,
                'ai_models': bot.get('models') or ['route through Buddy model policy; exact runtime model must be evidenced'],
                'apis_and_tools': bot.get('apis') or ['discover from API/tool registries and connection auditor'],
                'required_permissions': ['least privilege; derive from actual adapters/actions'],
                'pricing': {'declared': bot.get('priceRange'), 'revenue_model': bot.get('revenueModel'), 'status': 'proposal_until_approved_and_validated'},
                'demo': {'status': 'requires_sandbox_evidence', 'plan': 'show the bot completing a representative customer task end to end'},
                'website_or_landing_page': {'status': 'inherit_revenue_os_asset'},
                'sales_script': {'status': 'generate_from_verified_problem_value_proof_and_pricing'},
                'marketing_assets': {'status': 'select_from_500_method_advertising_catalog'},
                'referral_program': {'status': 'inherit_revenue_os'},
                'affiliate_program': {'status': 'inherit_revenue_os'},
                'knowledge_base': {'status': 'inherit_shared_reference_libraries_plus_bot_docs'},
                'faqs': {'status': 'generate_from customer objections, support evidence and known limits'},
                'kpis': ['task success', 'time saved', 'quality', 'latency', 'cost', 'qualified leads', 'conversion support', 'customer outcome', 'retention', 'support burden'],
                'verified_revenue': {'amount': None, 'status': 'read only from authorized verified payment events'},
                'customer_satisfaction': {'value': None, 'status': 'requires real authorized feedback evidence'},
                'version_history': {'source': 'git history and release evidence'},
                'roadmap': ['close measured capability gaps', 'close connection gaps', 'improve benchmark performance', 'validate sellable offer', 'graduate through live revenue gate'],
                'revenue_os': {
                    'ceo_orchestrator': REVENUE['ceo_orchestrator'],
                    'engines': REVENUE['engines'],
                    'specialist_bots': REVENUE['specialist_bots'],
                    'customer_journey': REVENUE['universal_customer_journey'],
                    'auto_provision': REVENUE['per_bot_auto_provision'],
                },
                'reference_libraries': STANDARD['automatic_inheritance']['reference_libraries'],
                'truth_boundary': STANDARD['truth_rule'],
            })
    payload = {
        'schema': 'dreamco.bot_business_blueprints.generated.v1',
        'bot_count': len(rows),
        'required_fields': STANDARD['required_fields'],
        'lean_business_loop': STANDARD['lean_business_loop'],
        'bots': rows,
        'truth_boundary': STANDARD['truth_rule'],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    lines = ['# Bot Business Blueprints', '', f'- Bots with generated blueprint: **{len(rows)}**', '', 'Every blueprint inherits the Revenue OS, shared reference libraries, advertising catalog and business/live-revenue gates.', '', '> Generated business assets remain proposals until repository, sandbox, market and runtime evidence passes.']
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'bots': len(rows), 'output': str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
