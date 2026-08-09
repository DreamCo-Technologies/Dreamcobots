#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'config/generated/business-billable-services-150.json'

SEED_30 = [
    'Discovery & Requirements', 'Industry Research', 'Competitor Analysis', 'Market Validation', 'Customer Persona Creation',
    'Business Model Design', 'Revenue Model Selection', 'Feature Planning', 'Workflow Design', 'System Architecture',
    'UI/UX Design', 'Branding', 'Domain & Naming', 'Prompt Engineering', 'AI Model Selection', 'Knowledge Base Creation',
    'API Integration Planning', 'Security Review', 'Compliance Review', 'Development', 'Testing', 'Bug Fixing',
    'Performance Optimization', 'Documentation', 'Deployment', 'Marketing Setup', 'Sales Funnel Setup', 'CRM Integration',
    'Analytics Setup', 'Maintenance & Support'
]

EXTENSIONS = {
    'Strategy & Validation': ['Problem Discovery', 'Customer Interviews', 'Demand Testing', 'Competitive Positioning', 'Feasibility Analysis', 'Risk Inventory', 'MVP Scope', 'Offer Design'],
    'Formation & Administration': ['Entity Choice Research', 'Formation Checklist', 'Ownership Structure', 'License Research', 'Permit Research', 'Tax Registration Support', 'Banking Setup Support', 'Insurance Needs Research'],
    'Finance': ['Budgeting', 'Forecasting', 'Cash Runway', 'Unit Economics', 'Pricing Experiments', 'Bookkeeping Setup', 'Billing Setup', 'Collections Workflow', 'Financial KPI Dashboard'],
    'Product & Technology': ['Product Requirements', 'Prototype', 'Database Design', 'API Design', 'Frontend Build', 'Backend Build', 'Mobile/PWA Build', 'Automation Build', 'Data Pipeline', 'Integration Testing'],
    'Operations': ['SOP Creation', 'Vendor Sourcing', 'Procurement Workflow', 'Inventory Workflow', 'Scheduling', 'Quality Management', 'Incident Response', 'Business Continuity', 'Cost Optimization'],
    'People': ['Hiring Plan', 'Job Description', 'Recruiting Support', 'Candidate Screening Workflow', 'Onboarding', 'Training Curriculum', 'Performance Scorecards', 'Workforce Automation Analysis'],
    'Marketing': ['SEO', 'AI Search Optimization', 'Content Strategy', 'Email Marketing', 'Social Marketing', 'Video Marketing', 'PR', 'Local Marketing', 'Event Marketing', 'Association Marketing', 'Partnership Marketing', 'Affiliate Marketing'],
    'Sales': ['Lead Discovery', 'Lead Enrichment', 'Contact Discovery', 'Qualification', 'Cold Email', 'LinkedIn Outreach', 'SMS Outreach', 'Voice Call Support', 'Appointment Setting', 'Sales Discovery', 'Demo', 'Proposal', 'Quote', 'Objection Handling', 'Closing Support'],
    'Customer Lifecycle': ['Customer Onboarding', 'Customer Support', 'Customer Success', 'Review Collection', 'Upsell', 'Cross-sell', 'Renewal', 'Referral Program', 'Affiliate Program', 'Win-back'],
    'Growth': ['New Channel Expansion', 'New Market Expansion', 'New Location Planning', 'Franchise Readiness', 'International Expansion', 'M&A Research', 'Acquisition Diligence Support', 'Succession Planning', 'Wind-down Support'],
    'Government': ['Government Contract Readiness', 'SAM.gov Opportunity Discovery', 'NAICS Mapping', 'PSC Mapping', 'Bid/No-bid Analysis', 'Capability Statement Support', 'Requirements Matrix', 'Government Proposal Support', 'Subcontractor Discovery', 'Past Performance Library'],
    'Nonprofit': ['Nonprofit Launch Support', 'Mission Design', 'Program Design', 'Grant Discovery', 'Grant Application Support', 'Donor CRM', 'Fundraising Campaign', 'Volunteer Management', 'Board Operations', 'Impact Measurement'],
    'Knowledge & Networks': ['Association Discovery', 'Chamber Discovery', 'Certification Research', 'Standards Research', 'Supplier Directory Research', 'Conference Discovery', 'Sponsorship Discovery', 'Investor Network Research'],
    'Creative Business': ['Book Production Pipeline', 'Film Production Pipeline', 'Music Production Pipeline', 'Creator Distribution', 'Rights/Metadata Workflow', 'Creative Marketing'],
}


def main() -> int:
    services = []
    seen = set()
    def add(name, category, source):
        key = name.casefold()
        if key in seen: return
        seen.add(key)
        services.append({
            'id': f'SVC-{len(services)+1:03d}', 'service': name, 'category': category, 'source': source,
            'can_be_sold_separately': True,
            'pricing_inputs': ['complexity', 'risk', 'human review', 'integrations', 'data volume', 'urgency', 'customer value'],
            'required_outputs': ['scope', 'inputs', 'deliverable', 'acceptance criteria', 'evidence', 'price or quote basis'],
            'status': 'service_blueprint'
        })
    for name in SEED_30: add(name, 'Owner-approved 30-step lifecycle', 'owner_approved_seed_30')
    for category, names in EXTENSIONS.items():
        for name in names:
            add(name, category, 'DreamCo lifecycle expansion')
            if len(services) >= 150: break
        if len(services) >= 150: break
    if len(services) < 150:
        # Create granular but meaningful implementation/review variants only as needed.
        for category, names in EXTENSIONS.items():
            for name in names:
                for suffix in (' Audit', ' Implementation'):
                    add(name + suffix, category, 'granular billable sub-stage')
                    if len(services) >= 150: break
                if len(services) >= 150: break
            if len(services) >= 150: break
    services = services[:150]
    payload = {
        'schema': 'dreamco.business_billable_services.generated.v1', 'service_count': len(services), 'seed_30_preserved': True,
        'rule': 'Every service can be quoted independently or bundled. Price is based on evidence and scope, not a universal hard-coded fee.',
        'services': services,
        'truth_boundary': 'A billable service blueprint is not proof a bot can deliver it autonomously. Delivery requires verified capability, applicable sandbox tests, permissions and professional review where required.'
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': len(services) == 150, 'services': len(services), 'output': str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if len(services) == 150 else 1

if __name__ == '__main__': raise SystemExit(main())
