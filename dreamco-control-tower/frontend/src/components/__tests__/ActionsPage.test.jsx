import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import ActionsPage from '../ActionsPage.jsx';

const libraryPayload = {
  bot_count: 1248,
  builders: [
    { id: 'full-bot-system', name: 'Full Bot System Builder', icon: '🤖', outputs: ['profile', 'api', 'webhook', 'sandbox'], approval: 'pull_request_required' },
    { id: 'apis-builder', name: 'API Builder', icon: '🔌', outputs: ['api', 'tests'], approval: 'pull_request_required' },
    { id: 'resources-builder', name: 'Resource Library Builder', icon: '📚', outputs: ['resource', 'tests'], approval: 'pull_request_required' },
  ],
  libraries: [
    { id: 'tools', name: 'Tools Library', icon: '🔧', count: 1248, description: 'Typed tools.' },
    { id: 'apis', name: 'Apis Library', icon: '🔌', count: 1248, description: 'Versioned APIs.' },
    { id: 'webhooks', name: 'Webhooks Library', icon: '🪝', count: 1248, description: 'Signed webhooks.' },
    { id: 'workflows', name: 'Workflows Library', icon: '🔁', count: 1248, description: 'Reusable workflows.' },
    { id: 'skills', name: 'Skills Library', icon: '🧠', count: 1248, description: 'Versioned skills.' },
    { id: 'sandboxes', name: 'Sandboxes Library', icon: '🧪', count: 1248, description: 'Isolated tests.' },
    { id: 'resources', name: 'Resources Library', icon: '📚', count: 1248, description: 'Per-bot starter resources.' },
  ],
  coverage: {
    bots_with_custom_api_contracts: 1248,
    bots_with_api_sandbox_bootcamps: 1248,
    bots_with_sandbox_workflow_generators: 1248,
    bots_with_owner_buddy_client_bootcamp_tracks: 1248,
    bots_with_top_ai_company_resource_seeds: 1248,
  },
  bootcamp_baseline: {
    name: 'World Class Bot Building Sandbox Bootcamp',
    audiences: ['owner', 'buddy', 'client'],
    sandbox_principles: ['hermetic_by_default', 'deterministic_fixtures', 'workflow_generated_per_test', 'human_approval_for_external_impact'],
    module_count: 7,
    top_ai_company_resource_seed_count: 100,
    source_boundaries: ['public_documentation_only', 'owner_approved_notes_only', 'no_private_or_proprietary_company_material'],
  },
};

const buddyCapabilityPayload = {
  generated_at: '2026-07-11T10:04:34.383589+00:00',
  summary: {
    bot_profiles_scanned: 1247,
    registry_division_count: 45,
    workflows: 40,
    test_files: 244,
    buddy_related_files: 179,
    buddy_related_bots: 14,
    build_states: {
      built_and_test_covered: 366,
      built_contract_ready: 874,
    },
    test_states: {
      ready_for_contract_testing: 874,
      ready_for_test_run: 368,
      needs_implementation_before_testing: 5,
    },
    coding_path_states: {
      needs_placeholder_review: 1109,
      needs_direct_test_coverage: 22,
      on_full_code_path: 109,
      needs_core_implementation: 5,
      needs_existing_system_mapping: 2,
    },
    bots_with_full_coding_path: 1247,
    all_bots_have_full_coding_path: true,
    production_readiness_states: {
      not_ready_placeholder_review: 1109,
      not_ready_needs_tests: 22,
      production_ready: 101,
      not_ready_missing_implementation: 7,
      production_candidate_approval_required: 8,
    },
    fully_coded_bots: 109,
    production_ready_bots: 101,
    all_bots_fully_coded: false,
    all_bots_production_ready: false,
    placeholder_marker_bots: 1109,
  },
  buddy_bots: [
    { slug: 'buddy-bot', name: 'Buddy Bot', division: 'CommandCore', description: 'Routes coding and testing across the fleet.', capabilities: ['Code generation', 'Cross-bot orchestration', 'Sandbox testing'], tests: ['tests/test_buddy_bot.py'], test_count: 1, build_state: 'built_and_test_covered', test_state: 'ready_for_test_run', production_readiness_status: 'production_ready', production_ready: true },
    { slug: 'buddy_core', name: 'Buddy Core', division: 'CommandCore', build_state: 'built_and_test_covered', test_state: 'ready_for_test_run' },
    { slug: 'buddy_orchestrator', name: 'Buddy Orchestrator', division: 'CommandCore', build_state: 'built_and_test_covered', test_state: 'ready_for_test_run' },
  ],
  bots: [
    { slug: 'buddy-bot', name: 'Buddy Bot', division: 'CommandCore', description: 'Routes coding and testing across the fleet.', capabilities: ['Code generation', 'Cross-bot orchestration', 'Sandbox testing'], tests: ['tests/test_buddy_bot.py'], test_count: 1, build_state: 'built_and_test_covered', test_state: 'ready_for_test_run', production_readiness_status: 'production_ready', production_ready: true, risk_hint: 'standard' },
    { slug: 'lead-gen-bot', name: 'Lead Generation Bot', division: 'DreamSalesPro', description: 'Finds and qualifies leads for sales workflows.', capabilities: ['Lead discovery', 'Prospect scoring', 'CRM enrichment'], tests: ['tests/generated_bot_smoke/test_lead_gen_bot_runtime.py'], test_count: 1, build_state: 'built_and_test_covered', test_state: 'ready_for_test_run', production_readiness_status: 'production_candidate_approval_required', production_ready: false, risk_hint: 'high' },
  ],
  attention: {
    needs_implementation: [
      { slug: 'payment_autocollector', name: 'Payment AutoCollector', division: 'DreamFinance' },
    ],
    needs_direct_test_coverage: [
      { slug: 'buddy-tool-builder', name: 'Buddy Tool Library Builder Bot', division: 'DreamCodeLab' },
    ],
    needs_existing_system_mapping: [
      { slug: 'ai_enablement_hub', name: 'AI Enablement Hub', division: 'DreamAIInfra' },
      { slug: 'elite_scraper', name: 'Elite Scraper', division: 'DreamSalesPro' },
    ],
  },
};

const githubTriagePayload = {
  generated_at: '2026-07-11T11:30:00+00:00',
  repo: 'DreamCo-Technologies/Dreamcobots',
  summary: {
    open_prs: 56,
    open_issues: 17,
    issue_comments_scanned: 100,
    pr_review_comments_scanned: 4,
    workflow_runs_scanned: 50,
    failed_workflow_runs: 6,
    active_workflow_runs: 2,
    pr_restart_queue: 12,
  },
  pr_restart_queue: [
    {
      number: 410,
      title: 'Finish Buddy readiness tracker',
      url: 'https://github.com/DreamCo-Technologies/Dreamcobots/pull/410',
      head_branch: 'buddy-readiness',
      age_days: 34,
      restart_reasons: ['stale_pr_needs_rebase_or_retest'],
    },
  ],
  failed_workflow_runs: [
    {
      id: 9001,
      name: 'System and Bot Builds Monitoring',
      branch: 'main',
      conclusion: 'failure',
      updated_at: '2026-07-11T11:10:00Z',
      url: 'https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/9001',
    },
  ],
};

const repositoryStewardshipPayload = {
  generated_at: '2026-07-11T12:00:00+00:00',
  repo: 'DreamCo-Technologies/Dreamcobots',
  summary: {
    open_prs: 56,
    open_issues: 17,
    ready_prs: 9,
    stale_prs: 47,
    stale_issues: 10,
    failed_workflow_runs: 6,
    restart_queue: 12,
    planned_close_prs: 1,
    planned_close_issues: 8,
    quality_checks: 3,
    failed_quality_checks: 0,
    skipped_quality_checks: 0,
    cleanroom_ready: false,
  },
  quality_checks: [
    { name: 'json_parse', status: 'pass', scanned: 200, failures: [] },
    { name: 'python_syntax', status: 'pass', scanned: 1000, failures: [] },
    { name: 'javascript_syntax', status: 'pass', scanned: 250, failures: [] },
  ],
  policy: {
    auto_close_without_owner_approval: false,
    auto_merge_without_green_checks: false,
    required_before_ready: [
      'json_parse',
      'python_syntax',
      'javascript_syntax',
      'workflow_failures_resolved_or_retested',
      'owner_approval_for_close_or_merge',
    ],
  },
  queues: {
    ready_prs: [],
    stale_prs: [],
    stale_issues: [],
    failed_workflow_runs: [],
    restart_queue: [],
  },
  cleanup_plan: {
    keep_prs: [],
    close_pr_candidates: [],
    keep_issues: [],
    close_issue_candidates: [],
  },
};

const buddyProductivityPayload = {
  generated_at: '2026-07-11T12:30:00+00:00',
  summary: {
    productivity_score: 82.5,
    bot_count: 1248,
    runtime_ready_bots: 1248,
    production_ready_bots: 1128,
    approval_gated_bots: 120,
    open_prs: 56,
    open_issues: 17,
    failed_workflow_runs: 24,
    failed_quality_checks: 0,
    estimated_monthly_savings_usd: 233,
    tracked_learning_loops: 4,
  },
  owner_productivity: {
    tracks: ['next best build task', 'repo cleanup burden', 'money-saving opportunities'],
    current_focus: ['Retest workflow blockers.', 'Review cost-saver findings.'],
  },
  client_productivity: {
    tracks: ['demo-ready bots', 'client-facing prospectus pages', 'safe sandbox test packets'],
    ready_to_show: ['Buddy Trust Layer', 'Actions dashboard', 'Repository cleanroom'],
  },
  bot_productivity: {
    tracks: ['runtime readiness', 'test readiness', 'learning-loop evidence'],
    coverage: {
      runtime_ready_percent: 100,
      production_ready_percent: 90.38,
      approval_gated_percent: 9.62,
    },
  },
  learning_loops: [
    { name: 'Capability inventory loop', helps: 'Buddy knows which bots are demo-ready, test-ready, and blocked.' },
    { name: 'Repository cleanroom loop', helps: 'Buddy keeps work queues organized before merge or client demo.' },
    { name: 'Cost saver loop', helps: 'Buddy points to lower-cost ways to keep the system running.' },
    { name: 'Platform audit loop', helps: 'Buddy packages bots as client-facing companies.' },
  ],
  next_actions: ['Prioritize workflow failures.', 'Turn top capabilities into client packages.'],
};

const releaseReadinessPayload = {
  schema: 'dreamco.release_readiness.v1',
  generated_at: '2026-07-14T12:00:00Z',
  branch: 'codex/bot-test-dashboard',
  mission: 'Make DreamCo reliable, demonstrable, and evidence-backed.',
  summary: {
    release_readiness_score: 73.91,
    first_ten_complete: 4,
    first_ten_active: 6,
    first_ten_blocked: 0,
    top_100_groups_complete: 1,
    top_100_groups_active: 5,
    top_100_groups_blocked: 0,
    open_prs: 56,
    open_issues: 17,
    failed_workflow_runs: 6,
    failed_quality_checks: 0,
    production_ready_bots: 101,
    bot_profiles_scanned: 1247,
    storage_ready: true,
    revenue_rescue_ready: false,
  },
  first_ten_updates: [
    { id: 'correct_registry_and_readme_counts', title: 'Correct registry and README counts', status: 'complete', proof: ['README truth copy'], missing: [], next: 'Keep all public claims tied to generated reports.' },
    { id: 'classify_all_profiles_by_implementation_status', title: 'Classify all profiles by implementation status', status: 'active', proof: ['Buddy inventory'], missing: ['Direct tests'], next: 'Normalize every profile with runtime, tests, permissions, and maturity evidence.' },
    { id: 'triage_open_pull_requests', title: 'Triage open pull requests', status: 'active', proof: ['GitHub triage report'], missing: [], next: 'Sort the open PR queue into merge, rebuild, replace, duplicate, and close candidates.' },
  ],
  top_100_groups: [
    { id: 'repository_stability', title: 'Repository Stability', planned_updates: 20, status: 'active', metrics: { open_prs: 56 }, focus: [], first_move: 'Make one required CI workflow.', next: 'Use the cleanroom queue to reduce stale PRs and failed workflow runs.' },
    { id: 'public_docs_identity', title: 'Public Docs Identity', planned_updates: 15, status: 'complete', metrics: {}, focus: [], first_move: 'Keep README claims tied to measurable evidence.', next: 'Refresh docs from generated evidence instead of manual claims.' },
  ],
  already_done: [],
  currently_building: [],
  blocked_or_unproven: [],
  next_actions: [
    'Refresh capability, stewardship, storage, Stripe, and bot connection reports before every release PR.',
    'Reduce the PR restart queue before adding more bots or major dashboard surfaces.',
  ],
};

const storageGuardPayload = {
  schema: 'dreamco.storage_guard.v1',
  generated_at: '2026-07-12T00:00:00Z',
  summary: {
    storage_ready: true,
    checks: 55,
    failed_checks: 0,
    warnings: 0,
    memory_tiers: 4,
    partitioning_rules: 7,
    compaction_rules: 6,
    useful_keep_categories: 10,
    useful_drop_categories: 10,
    useful_required_metadata: 8,
    approval_gates: 11,
    largest_resource_shard_mb: 10.517,
    largest_resource_shard: 'config/generated/system_libraries/resources/dreamcodelab.json',
    resource_shard_count: 45,
    bot_resource_entries_checked: 1248,
  },
  budgets: {
    generated_resource_shard_max_mb: 25,
  },
  memory_tiers: [
    { tier: 'hot', purpose: 'Active task memory and recent bot context.', rollover_at_mb: 128 },
    { tier: 'warm', purpose: 'Approved lessons and reusable skill memory.', rollover_at_mb: 256 },
    { tier: 'cold', purpose: 'Compressed audit archives and long-term evidence.', rollover_at_mb: 512 },
    { tier: 'vector', purpose: 'Searchable memory references with partitioned vectors.', rollover_at_mb: 256 },
  ],
  partitioning_rules: [
    'Never store all bot resources, memories, events, vectors, or source snapshots in one monolithic file.',
  ],
  useful_data_policy: {
    rule: 'Only store data that can improve owner decisions, client delivery, bot learning, debugging, compliance, or reproducible rebuilds.',
    keep_categories: ['failure_summaries_with_retest_commands', 'build_rebuild_and_debug_packets'],
    drop_categories: ['duplicate_records', 'raw_scratchpads_after_summary', 'low_signal_chat_fillers'],
    required_metadata: ['source', 'usefulness_reason', 'retention_tier', 'dedupe_key', 'redaction_state'],
    minimum_usefulness_score_to_store: 3,
  },
  checks: [{ name: 'resource_sharding_integrity', status: 'pass', message: 'resources are sharded and count-safe' }],
  warnings: [],
};

const appFoundryPayload = {
  schema: 'dreamco.app_foundry_readiness.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Make DreamCo the in-house A-to-Z foundry for building, testing, packaging, hosting, and deploying games, websites, apps, school courses, simulations, dashboards, creative media, and business bot systems.',
  ownership_rule: 'DreamCo-owned repository code is the source of truth. External hosts and services are deployment targets or adapters, not the builder of record.',
  operating_posture: 'sandbox_first_pull_request_review',
  summary: {
    readiness_score: 100,
    creation_lanes: 8,
    in_house_systems: 18,
    deployment_targets: 6,
    static_or_configured_targets: 4,
    planned_runtime_targets: 2,
    bot_count: 1248,
    custom_api_contracts: 1248,
    api_sandbox_bootcamps: 1248,
    sandbox_workflow_generators: 1248,
    storage_ready: true,
    live_deploy_requires_owner_approval: true,
  },
  lanes: [
    { id: 'games', label: 'Games', description: 'Prompt-to-playable prototypes with design docs.', output_count: 7, outputs: ['game_design_doc', 'playable_prototype', 'test_plan'], host_targets: ['github_pages', 'static_host'], approval_gates: ['asset_rights'], status: 'ready_for_sandbox_preview' },
    { id: 'websites', label: 'Websites', description: 'Client-ready websites and product showcases.', output_count: 7, outputs: ['site_map', 'responsive_ui', 'deployment_bundle'], host_targets: ['github_pages', 'hostinger'], approval_gates: ['brand_claim_review'], status: 'ready_for_sandbox_preview' },
    { id: 'apps', label: 'Apps', description: 'Full app builds with APIs, tests, and rollback notes.', output_count: 7, outputs: ['product_spec', 'data_model', 'test_suite'], host_targets: ['local_laptop', 'managed_node_host'], approval_gates: ['credential_owner_approval'], status: 'ready_for_sandbox_preview' },
    { id: 'school_courses', label: 'School courses', description: 'Course generators for lessons, quizzes, and teacher notes.', output_count: 7, outputs: ['course_outline', 'lesson_modules', 'quizzes'], host_targets: ['github_pages', 'course_export'], approval_gates: ['minor_safety'], status: 'ready_for_sandbox_preview' },
    { id: 'simulations', label: 'Simulations', description: 'Adjustable business and science simulations.', output_count: 6, outputs: ['scenario_model', 'simulation_engine', 'results_dashboard'], host_targets: ['github_pages', 'container_host'], approval_gates: ['no_guaranteed_outcome_claims'], status: 'ready_for_sandbox_preview' },
    { id: 'dashboards', label: 'Dashboards', description: 'Operational command centers and KPI trackers.', output_count: 6, outputs: ['metric_catalog', 'status_cards', 'alert_rules'], host_targets: ['github_pages', 'hostinger'], approval_gates: ['private_data_redaction'], status: 'ready_for_sandbox_preview' },
    { id: 'creative_media', label: 'Creative media', description: 'Music video packets and image workflows.', output_count: 7, outputs: ['concept', 'storyboard', 'rights_log'], host_targets: ['static_preview'], approval_gates: ['written_consent_for_likeness'], status: 'ready_for_sandbox_preview' },
    { id: 'business_bots', label: 'Business bots', description: 'Client business workers and approval packets.', output_count: 7, outputs: ['bot_prospectus', 'tool_contracts', 'approval_packet'], host_targets: ['local_laptop'], approval_gates: ['money_movement_approval'], status: 'ready_for_sandbox_preview' },
  ],
  deployment_targets: [
    { id: 'github_pages', label: 'GitHub Pages', role: 'Free static previews for dashboards, websites, courses, simple games, and static simulations.', status: 'ready_for_static_frontend' },
    { id: 'hostinger', label: 'Hostinger', role: 'Starter public hosting target for Buddy dashboard builds and client demos.', status: 'configured_adapter' },
    { id: 'local_laptop', label: 'Local laptop', role: 'Development, demos, sandbox runs, and owner-supervised builds before public deployment.', status: 'ready' },
    { id: 'managed_node_host', label: 'Managed Node host', role: 'Node or API-backed apps after secrets and rollback gates are configured.', status: 'planned_adapter' },
  ],
  quality_gates: ['all_generated_code_builds', 'sandbox_test_packet_exists', 'no_secrets_committed', 'owner_approval_before_live_money_outreach_or_deploy'],
  next_build_targets: ['Create one prompt-to-preview wizard for all eight lanes.'],
  gaps: [],
};

const botFounderAppStorePayload = {
  schema: 'dreamco.bot_founder_app_store_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Every DreamCo bot studies its market, designs a useful autonomous app, prepares a safe company plan, and packages itself for the DreamCo app store.',
  live_action_policy: 'Bots may research, draft, score, package, simulate, and propose. Bots must not contact customers, run ads, spend money, deploy publicly, move money, create fake claims, or publish app-store listings without owner approval.',
  summary: {
    bot_count: 1248,
    founder_packets: 1248,
    bots_with_app_concept: 1248,
    bots_with_competitor_study_plan: 1248,
    bots_with_revenue_model: 1248,
    bots_with_marketing_plan: 1248,
    bots_with_customer_discovery_plan: 1248,
    bots_with_app_store_listing: 1248,
    bots_with_sandbox_test_plan: 1248,
    bots_blocked_from_live_actions_until_approval: 1248,
    app_store_categories: 12,
    study_loops: 7,
    approval_gates: 11,
  },
  founder_study_loops: [
    { id: 'competition_lab', label: 'Competition Lab', purpose: 'Study public competitors, pricing, feature gaps, reviews, and customer complaints.', outputs: ['competitor_map', 'feature_gap_matrix', 'pricing_notes'] },
    { id: 'autonomous_money_lab', label: 'Autonomous Money Lab', purpose: 'Find ethical value creation, offer packaging, pricing tests, cost savings, and revenue recovery ideas.', outputs: ['revenue_model', 'offer_stack', 'risk_disclosures'] },
    { id: 'app_builder_lab', label: 'App Builder Lab', purpose: 'Design one app-store-ready product with user, workflow, demo, sandbox test, and deployment plan.', outputs: ['app_concept', 'mvp_scope', 'deployment_plan'] },
  ],
  app_store_categories: [
    { category: 'business_automation', bot_count: 300 },
    { category: 'developer_tools', bot_count: 152 },
    { category: 'sales_and_marketing', bot_count: 88 },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      emoji: '🤝',
      app_store_category: 'business_automation',
      target_customer: 'DreamCo owners and client teams',
      autonomous_app_concept: { name: 'Buddy Bot App', promise: 'A supervised command center for safe AI company building.' },
      app_store_listing: { status: 'draft_ready_for_owner_review' },
    },
  ],
  approval_gates: ['customer_outreach', 'ad_spend', 'public_deployment', 'payment_collection', 'money_movement', 'app_store_publish'],
};

const scaling24Payload = {
  schema: 'dreamco.24_hour_scaling_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Keep DreamCo improving around the clock through safe 24-hour research, build, test, app-store, and approval cycles.',
  default_mode: 'continuous_supervised_scaling',
  summary: {
    readiness_score: 100,
    cycles_defined: 6,
    safe_automation_steps: 24,
    cycle_approval_steps: 28,
    always_blocked_gates: 11,
    scale_lanes: 12,
    bot_founder_packets: 1248,
    app_store_categories: 12,
    app_foundry_lanes: 8,
    storage_ready: true,
    min_replicas: 2,
    max_replicas: 20,
    self_healing_enabled: true,
  },
  daily_cycles: [
    { id: 'market_research_cycle', window: '00:00-03:00', purpose: 'Study competitors, app-store ideas, customer problems, pricing, reviews, and market gaps.', safe_automation: ['public_source_queue', 'competitor_notes'], approval_required: ['customer_contact'] },
    { id: 'build_cycle', window: '03:00-07:00', purpose: 'Turn top opportunities into app concepts and pull-request-safe tasks.', safe_automation: ['app_concept_generation', 'mvp_scope'], approval_required: ['production_deploy'] },
    { id: 'test_cycle', window: '07:00-11:00', purpose: 'Run syntax checks, smoke tests, API sandbox tests, and dashboard health checks.', safe_automation: ['sandbox_tests', 'report_refresh'], approval_required: ['live_api_mutation'] },
    { id: 'growth_cycle', window: '15:00-19:00', purpose: 'Prepare ethical marketing, customer discovery, launch experiments, SEO briefs, and outreach drafts.', safe_automation: ['content_drafts', 'lead_scoring'], approval_required: ['ad_spend'] },
  ],
  scale_lanes: ['bot_founder_packets', 'app_store_listing_drafts', 'sandbox_bootcamps', 'competitor_research'],
  always_blocked_without_owner_approval: ['customer_outreach', 'ad_spend', 'money_movement', 'public_deployment', 'app_store_publish'],
};

const specializedKnowledgePayload = {
  schema: 'dreamco.specialized_bot_knowledge_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Give every DreamCo bot a specialized knowledge system for its division, customers, competitors, app-store product, workflows, safety gates, and learning loop.',
  default_mode: 'local_first_source_backed_learning',
  summary: {
    bot_count: 1248,
    knowledge_profiles: 1248,
    knowledge_domains: 9,
    bots_with_all_knowledge_domains: 1248,
    bots_with_source_policy: 1248,
    bots_with_memory_policy: 1248,
    bots_with_runtime_tooling_knowledge: 1248,
    bots_with_safety_approval_knowledge: 1248,
    bots_with_app_builder_knowledge: 1248,
    resource_library_bot_count: 1248,
    bot_founder_packets: 1248,
    storage_ready: true,
    approval_gates: 10,
    memory_tiers: 4,
  },
  knowledge_domains: [
    { id: 'domain_expertise', label: 'Domain Expertise', purpose: 'Know the bot industry, job, terminology, workflows, metrics, regulations, and common failure modes.' },
    { id: 'customer_intelligence', label: 'Customer Intelligence', purpose: 'Know who the bot helps and what outcome they care about.' },
    { id: 'competitor_intelligence', label: 'Competitor Intelligence', purpose: 'Study public competitors, substitutes, pricing, feature gaps, reviews, positioning, onboarding, and trust signals.' },
    { id: 'app_builder_knowledge', label: 'App Builder Knowledge', purpose: 'Know how to turn the bot into a usable app, website, course, game, simulation, dashboard, or workflow.' },
  ],
  source_policy: {
    allowed: ['public documentation', 'public pricing pages', 'owner-approved notes', 'test reports'],
    blocked: ['secrets', 'private account data without approval', 'copied proprietary code'],
  },
  memory_tiers: [
    { id: 'hot', purpose: 'Active task context and short-lived work notes.' },
    { id: 'warm', purpose: 'Approved lessons and reusable workflows.' },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      emoji: '🤝',
      division: 'CommandCore',
      target_customer: 'DreamCo owners and client teams',
      app_concept_name: 'Buddy Bot App',
      specialized_study_queue: ['Map customer pains, buying triggers, and proof needs.', 'Compare public competitors and substitute workflows.'],
    },
  ],
};

const aiAgentModelLibraryPayload = {
  schema: 'dreamco.buddy_ai_agent_model_library_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Give Buddy a governed prompt, tool, agent, and model-resource library so every bot can pick the best AI route for each task.',
  policy: {
    model_id_rule: 'Provider model IDs, prices, rate limits, and availability change often. Verify the current provider model ID before production use.',
    approval_rule: 'External sends, paid calls, production deploys, customer data, money movement, likeness cloning, and account changes require owner approval.',
  },
  summary: {
    model_resources: 100,
    providers: 25,
    agent_types: 16,
    prompt_types: 20,
    tool_types: 23,
    task_routes: 30,
    bot_count: 1248,
    bots_with_model_routing: 1248,
    resources_requiring_model_id_verification: 100,
    approval_gated_resources: 100,
  },
  model_resources: [
    {
      id: 'openai_reasoning__quality',
      provider: 'OpenAI',
      label: 'OpenAI reasoning and general intelligence - Best Quality',
      tier: 'quality',
      good_at: ['complex planning', 'code repair', 'tool calling'],
      bad_at: ['unverified current facts without retrieval', 'tasks needing disabled credentials'],
    },
  ],
  task_routes: [
    { task_type: 'coding', primary_resource: 'openai_reasoning__quality', fallback_resources: ['deepseek_coder_reasoner__quality'], required_evals: ['task_success', 'cost_latency'] },
    { task_type: 'image_generation', primary_resource: 'openai_image__quality', fallback_resources: ['black_forest_image__quality'], required_evals: ['task_success', 'safety_gate'] },
  ],
  agent_prompt_tool_matrix: [
    { agent_type: 'coding_agent', label: 'Coding Agent', prompt_types: ['task_brief', 'tool_contract'], tool_types: ['file_reader', 'code_editor'] },
    { agent_type: 'model_router_agent', label: 'Model Router Agent', prompt_types: ['task_brief', 'rubric_eval'], tool_types: ['vector_search', 'approval_gate'] },
  ],
};

const businessLaunchExpansionPayload = {
  schema: 'dreamco.business_launch_expansion_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Help clients start, improve, relocate, publish, market, staff, supply, and expand businesses through Buddy-governed bot teams and permissioned custom sub-agents.',
  positioning: 'DreamCo is the A-to-Z business launch and expansion operating system.',
  summary: {
    bot_count: 1248,
    service_lanes_ready: 10,
    sub_agent_roles_ready: 10,
    client_workflows_ready: 10,
    approval_gates_declared: 12,
    professional_review_blocks: 6,
    deliverables_declared: 40,
    lane_test_packets: 10,
    all_lanes_permissioned: true,
  },
  permission_model: {
    default_mode: 'draft_research_and_prepare_only',
    client_must_approve: ['sub_agent_creation', 'domain_purchase', 'business_registration_filing', 'app_store_submission'],
  },
  service_lanes: [
    { id: 'business_formation', label: 'Business Formation', purpose: 'Prepare business name checks, registration checklist, permits checklist, and launch timeline.', deliverables: ['entity_options_brief', 'registration_checklist'], approval_gates: ['business_registration_filing'] },
    { id: 'domains_and_brand', label: 'Domains and Brand', purpose: 'Find domain options, social handles, brand kit, and website launch plan.', deliverables: ['domain_shortlist', 'brand_brief'], approval_gates: ['domain_purchase'] },
    { id: 'supplier_network', label: 'Supplier Network', purpose: 'Find supplier categories, prepare RFQ packets, and compare terms.', deliverables: ['supplier_shortlist', 'rfq_packet'], approval_gates: ['customer_or_supplier_outreach'] },
  ],
  sub_agent_roles: [
    { id: 'business_formation_agent', label: 'Business Formation Agent', can_prepare: ['name research', 'entity comparison notes'], cannot_do_without_approval: ['file registrations'] },
    { id: 'domain_brand_agent', label: 'Domain and Brand Agent', can_prepare: ['domain shortlist', 'brand kit'], cannot_do_without_approval: ['buy domains'] },
  ],
};

const botContractDiscoveryPayload = {
  schema: 'dreamco.bot_contract_discovery_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Make every DreamCo bot continuously search for contract, grant, RFP, procurement, partnership, supplier, app-store, and service opportunities.',
  default_mode: 'public_source_discovery_and_draft_only',
  summary: {
    bot_count: 1248,
    bots_with_contract_discovery: 1248,
    opportunity_types_tracked: 12,
    source_categories_tracked: 4,
    approval_gates_declared: 12,
    blocked_actions_declared: 7,
    matching_fields: 13,
    bot_contract_roles: 8,
    sample_opportunities_ready: 12,
    all_bots_ready_for_contract_search: true,
  },
  opportunity_types: ['government_contract', 'private_rfp', 'grant', 'supplier_contract', 'trucking_route_contract'],
  source_categories: [
    { id: 'public_procurement', label: 'Public Procurement', examples: ['federal opportunity portals', 'state procurement portals'], allowed_actions: ['search', 'summarize', 'score'] },
    { id: 'private_rfp_sources', label: 'Private RFP Sources', examples: ['company vendor pages'], allowed_actions: ['search', 'prepare outreach draft'] },
  ],
  approval_gates: ['submit_bid', 'contact_buyer', 'contact_supplier', 'sign_contract', 'spend_money'],
  top_opportunity_types: [
    { opportunity_type: 'client_service_opportunity', bot_count: 1248 },
    { opportunity_type: 'private_rfp', bot_count: 1248 },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      opportunity_types: ['client_service_opportunity', 'private_rfp'],
      sample_search_prompt: 'Search public and owner-approved sources for Buddy Bot contract opportunities.',
    },
  ],
};

const aiDataPackageLibraryPayload = {
  schema: 'dreamco.ai_data_package_library_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Create governed AI data packages that DreamCo can sell or license for model training, fine-tuning, retrieval, benchmarking, evaluation, and agent simulation.',
  positioning: 'DreamCo sells rights-cleared, quality-scored, metadata-rich AI data packages.',
  langchain: {
    required: true,
    javascript_packages: ['langchain', '@langchain/core', 'zod'],
    use_cases: ['document loading', 'chunking', 'metadata normalization', 'retrieval datasets'],
  },
  summary: {
    bot_count: 1248,
    bot_package_blueprints: 1248,
    package_types_ready: 12,
    quality_gates_ready: 12,
    commercial_models_ready: 7,
    approval_gates: 9,
    required_rights_metadata: 14,
    allowed_source_types: 7,
    blocked_source_types: 8,
    langchain_ready: true,
    langchain_packages: 3,
    sellable_package_samples: 12,
  },
  package_types: [
    { id: 'instruction_tuning', label: 'Instruction Tuning', buyer_use: 'Improve task following and business workflow agents.', formats: ['jsonl', 'parquet'] },
    { id: 'rag_knowledge_base', label: 'RAG Knowledge Base', buyer_use: 'Power retrieval systems with chunked documents.', formats: ['jsonl', 'markdown'] },
  ],
  quality_gates: ['rights_clearance', 'pii_scan', 'deduplication', 'schema_validation'],
  commercial_models: ['one_time_dataset_license', 'subscription_data_feed'],
  approval_gates: ['sell_or_license_dataset', 'use_client_data', 'publish_sample_records'],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      package_types: ['instruction_tuning', 'eval_benchmark'],
      sample_package_name: 'Buddy Bot Training and Eval Data Pack',
      sample_buyer_use: 'Train, evaluate, or retrieve knowledge for CommandCore workflows.',
    },
  ],
};

const peopleJobQualificationPayload = {
  schema: 'dreamco.people_job_qualification_report.v1',
  generated_at: '2026-07-15T00:00:00Z',
  mission: 'Give Buddy a governed people-search and job-qualification lookup system for recruiting, client discovery, contractor matching, partner research, and workforce planning.',
  default_mode: 'public_or_owner_approved_research_only',
  summary: {
    bot_count: 1248,
    bot_people_lookup_blueprints: 1248,
    qualification_lanes_ready: 6,
    approval_gates_declared: 12,
    blocked_uses_declared: 8,
    allowed_source_types: 8,
    blocked_source_types: 10,
    privacy_metadata_fields: 9,
    qualification_scoring_factors: 7,
    buddy_bot_roles: 8,
    human_review_required: true,
  },
  privacy_policy: {
    allowed_sources: ['self-provided resume or profile', 'owner-approved CRM records', 'public professional profiles'],
    blocked_sources: ['private accounts without approval', 'protected-class inference'],
  },
  qualification_lanes: [
    { id: 'candidate_resume_match', label: 'Candidate Resume Match', purpose: 'Compare self-provided resumes against a job description.', outputs: ['skills_match', 'experience_evidence'] },
    { id: 'contractor_vendor_match', label: 'Contractor and Vendor Match', purpose: 'Research public contractor/vendor profiles and capabilities.', outputs: ['vendor_shortlist', 'capability_match'] },
  ],
  approval_gates: ['collect_personal_data', 'contact_person', 'make_hiring_decision'],
  blocked_uses: ['automated_hiring_or_rejection', 'protected_class_scoring'],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      qualification_lanes: ['candidate_resume_match', 'employee_role_fit'],
      sample_lookup_prompt: 'Prepare a privacy-safe people or job-qualification lookup packet for Buddy Bot.',
    },
  ],
};

const stripeRevenueRescuePayload = {
  schema: 'dreamco.stripe_revenue_rescue.v1',
  generated_at: '2026-07-12T00:00:00Z',
  summary: {
    revenue_rescue_ready: false,
    checkout_ready_offers: 0,
    offers_checked: 2,
    tracked_events: 0,
    gross_revenue_cents: 0,
    checkout_completed: 0,
    payment_succeeded: 0,
    invoice_paid: 0,
    payment_email_recipients: 0,
    payment_email_notices: 0,
    payment_email_sent: 0,
    github_payment_notifications_enabled: false,
    github_payment_issues_created: 0,
    blocker_count: 6,
  },
  revenue_blockers: [
    'No checkout-ready live Stripe offers with price and payment link IDs.',
    'Payment alert email recipients are not configured.',
    'GitHub payment notifications are not enabled.',
  ],
  priority_fixes: ['Create or confirm two live Stripe Payment Links for the starter audit and monthly command center offers.'],
  offers: [],
  safety_note: 'This report never prints secret values.',
};

const productionApprovalPacketsPayload = {
  schema: 'dreamco.production_approval_packets.v1',
  generated_at: '2026-07-14T13:00:00Z',
  summary: {
    approval_packets: 120,
    live_approved: 0,
    approval_required: 120,
    smoke_tests_passed: 1248,
    smoke_tests_failed: 0,
    sandbox_safe_production_candidates: 120,
    full_live_production_ready_after_approval: 0,
  },
  required_buddy_money_request: 'Buddy, help me make money with this bot. I approve the listed live actions and understand the risks.',
  risk_breakdown: {
    money_movement: 42,
    financial_or_trading: 31,
    security_or_defense: 20,
  },
  packets: [],
  next_actions: [
    'Review the approval-required bots by risk category before enabling live actions.',
    'Approve only the specific live actions each bot is allowed to perform.',
    'Keep risky external actions blocked until owner approval is recorded.',
  ],
};

const buddyOpsPayload = {
  schema: 'dreamco.buddy_ops_queue.v1',
  count: 1,
  operations: [
    {
      id: 'buddy-op-existing',
      builder: 'Stripe Revenue Rescue Builder',
      operation_type: 'revenue_operation',
      prompt: 'Fix Stripe checkout notifications',
      mode: 'sandbox_first_pull_request_review',
    },
  ],
};

const buddyBotConnectionsPayload = {
  schema: 'dreamco.buddy_bot_connection_guard.v1',
  generated_at: '2026-07-14T00:00:00Z',
  summary: {
    all_bots_connected_to_buddy: true,
    all_bots_testable_from_actions_page: true,
    all_bots_have_custom_resources: true,
    all_bots_ready: true,
    bot_count: 1248,
    buddy_connected_bots: 1248,
    actions_page_testable_bots: 1248,
    custom_resource_ready_bots: 1248,
    failed_bots: 0,
    resources_per_bot_required: 100,
  },
  failures: [],
};

const buddyPromptResponse = {
  packet: {
    id: 'buddy-op-test',
    builder: 'Full Bot System Builder',
    operation_type: 'bot_system_operation',
    prompt: 'build a new bot system',
    mode: 'sandbox_first_pull_request_review',
    outputs: ['implementation plan', 'sandbox test evidence'],
  },
};

function StubActionsMonitor() {
  return <div>Actions monitor panel</div>;
}

beforeEach(() => {
  global.fetch = vi.fn((url, options = {}) => {
    if (url === '/api/buddy-ops/prompt' && options.method === 'POST') {
      return Promise.resolve({
        ok: true,
        status: 201,
        json: async () => buddyPromptResponse,
      });
    }
    let payload = libraryPayload;
    if (url === '/api/buddy-capabilities') payload = buddyCapabilityPayload;
    if (url === '/api/github-triage') payload = githubTriagePayload;
    if (url === '/api/repository-stewardship') payload = repositoryStewardshipPayload;
    if (url === '/api/buddy-productivity') payload = buddyProductivityPayload;
    if (url === '/api/release-readiness') payload = releaseReadinessPayload;
    if (url === '/api/app-foundry') payload = appFoundryPayload;
    if (url === '/api/bot-founder-app-store') payload = botFounderAppStorePayload;
    if (url === '/api/24-hour-scaling') payload = scaling24Payload;
    if (url === '/api/specialized-bot-knowledge') payload = specializedKnowledgePayload;
    if (url === '/api/ai-agent-model-library') payload = aiAgentModelLibraryPayload;
    if (url === '/api/business-launch-expansion') payload = businessLaunchExpansionPayload;
    if (url === '/api/bot-contract-discovery') payload = botContractDiscoveryPayload;
    if (url === '/api/ai-data-package-library') payload = aiDataPackageLibraryPayload;
    if (url === '/api/people-job-qualification') payload = peopleJobQualificationPayload;
    if (url === '/api/storage-guard') payload = storageGuardPayload;
    if (url === '/api/stripe-revenue-rescue') payload = stripeRevenueRescuePayload;
    if (url === '/api/production-approval-packets') payload = productionApprovalPacketsPayload;
    if (url === '/api/buddy-ops') payload = buddyOpsPayload;
    if (url === '/api/buddy-bot-connections') payload = buddyBotConnectionsPayload;
    return Promise.resolve({
      ok: true,
      json: async () => payload,
    });
  });
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe('ActionsPage', () => {
  it('renders the system builder hub and live coverage', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    expect(screen.getByText('Buddy Command Tower for building, testing, and presenting bot systems')).toBeInTheDocument();
    expect(screen.getByText('Operational status')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Recent Buddy operations' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Operational proof' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Make the current system reliable, organized, and demonstrable' })).toBeInTheDocument();
    expect(screen.getByText('Verify the repository')).toBeInTheDocument();
    expect(screen.getByText('Complete the bot inventory')).toBeInTheDocument();
    expect(screen.getByText('Pick five sellable bots')).toBeInTheDocument();
    expect(screen.getByText('Sunday night milestone')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Convert the repository into one reliable operating platform' })).toBeInTheDocument();
    expect(screen.getByText('Stabilize repository')).toBeInTheDocument();
    expect(screen.getByText('Prove every bot')).toBeInTheDocument();
    expect(screen.getByText('Make Buddy real control')).toBeInTheDocument();
    expect(screen.getByText('Make five bot products work end to end')).toBeInTheDocument();
    expect(screen.getByText('Top 100 update backlog')).toBeInTheDocument();
    expect(screen.getByText('100 updates mapped')).toBeInTheDocument();
    expect(screen.getByText('Done versus still-building comparison')).toBeInTheDocument();
    expect(screen.getByText('First ten execution proof')).toBeInTheDocument();
    expect(screen.getByText('Top 100 group state')).toBeInTheDocument();
    expect(screen.getByText('Buddy next moves')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('73.91')).toBeInTheDocument());
    expect(screen.getByText('Repository stability')).toBeInTheDocument();
    expect(screen.getByText('Bot truth registry')).toBeInTheDocument();
    expect(screen.getAllByText('Trustworthy autonomy').length).toBeGreaterThan(0);
    expect(screen.getByRole('heading', { name: 'Professional delivery pipeline' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Prompt Buddy from the Actions page' })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Stripe Revenue Rescue Builder')).toBeInTheDocument());
    expect(screen.getByRole('heading', { name: 'AI Creation Studio for apps, games, simulations, media, and business systems' })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'In-house A-to-Z builder, host, and deploy system' })).toBeInTheDocument());
    expect(screen.getByText('Own-code-first rule')).toBeInTheDocument();
    expect(screen.getByText('Games')).toBeInTheDocument();
    expect(screen.getByText('Websites')).toBeInTheDocument();
    expect(screen.getByText('Apps')).toBeInTheDocument();
    expect(screen.getAllByText('School courses').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Simulations').length).toBeGreaterThan(0);
    expect(screen.getByText('Deployment targets')).toBeInTheDocument();
    expect(screen.getAllByText('GitHub Pages').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Hostinger').length).toBeGreaterThan(0);
    expect(screen.getByText('Live deploy gates')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Every bot studies the market and prepares its own autonomous app business' })).toBeInTheDocument());
    expect(screen.getByText('Bot Founder App Store')).toBeInTheDocument();
    expect(screen.getByText('Live-action approval wall')).toBeInTheDocument();
    expect(screen.getByText('Competition Lab')).toBeInTheDocument();
    expect(screen.getByText('Autonomous Money Lab')).toBeInTheDocument();
    expect(screen.getByText('App Builder Lab')).toBeInTheDocument();
    expect(screen.getByText('Sample bot-owned app-store packets')).toBeInTheDocument();
    expect(screen.getByText('A supervised command center for safe AI company building.')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Around-the-clock research, build, test, package, growth, and review cycles' })).toBeInTheDocument());
    expect(screen.getByText('24-hour scaling system')).toBeInTheDocument();
    expect(screen.getByText('Market Research Cycle')).toBeInTheDocument();
    expect(screen.getByText('Build Cycle')).toBeInTheDocument();
    expect(screen.getByText('Always blocked without approval')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Every bot gets its own source-backed knowledge system' })).toBeInTheDocument());
    expect(screen.getByText('Specialized bot knowledge')).toBeInTheDocument();
    expect(screen.getByText('Domain Expertise')).toBeInTheDocument();
    expect(screen.getByText('Competitor Intelligence')).toBeInTheDocument();
    expect(screen.getAllByText('Source policy').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Memory tiers').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Sample specialized knowledge profiles')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Buddy picks the best AI route for every task' })).toBeInTheDocument());
    expect(screen.getByText('Prompt, tool, agent, and model library')).toBeInTheDocument();
    expect(screen.getByText('Best task routes')).toBeInTheDocument();
    expect(screen.getByText('Agent harness')).toBeInTheDocument();
    expect(screen.getByText('Model strengths and weaknesses')).toBeInTheDocument();
    expect(screen.getByText('OpenAI reasoning and general intelligence - Best Quality')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Buddy coordinates everything a business needs to start, improve, or expand' })).toBeInTheDocument());
    expect(screen.getByText('Business launch and expansion OS')).toBeInTheDocument();
    expect(screen.getByText('A-to-Z business service lanes')).toBeInTheDocument();
    expect(screen.getByText('Business Formation')).toBeInTheDocument();
    expect(screen.getByText('Domains and Brand')).toBeInTheDocument();
    expect(screen.getByText('Supplier Network')).toBeInTheDocument();
    expect(screen.getByText('Custom sub-agent roles')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Every bot searches for contracts and opportunity paths' })).toBeInTheDocument());
    expect(screen.getByText('Always-on contract discovery')).toBeInTheDocument();
    expect(screen.getByText('Contract opportunity types')).toBeInTheDocument();
    expect(screen.getByText('Public Procurement')).toBeInTheDocument();
    expect(screen.getByText('Approval wall')).toBeInTheDocument();
    expect(screen.getByText('Sample bot contract scouts')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Rights-cleared data products for model training and evals' })).toBeInTheDocument());
    expect(screen.getByText('AI data package library')).toBeInTheDocument();
    expect(screen.getByText('Sellable data package types')).toBeInTheDocument();
    expect(screen.getByText('LangChain ready')).toBeInTheDocument();
    expect(screen.getByText('Instruction Tuning')).toBeInTheDocument();
    expect(screen.getByText('Buddy Bot Training and Eval Data Pack')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Buddy prepares privacy-safe people and role-fit lookup packets' })).toBeInTheDocument());
    expect(screen.getByText('People search and job qualification')).toBeInTheDocument();
    expect(screen.getByText('Qualification lookup lanes')).toBeInTheDocument();
    expect(screen.getByText('Candidate Resume Match')).toBeInTheDocument();
    expect(screen.getAllByText('Allowed sources').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Sample people lookup bot packets')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'AI company builder with human trust built in' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Tracks what helps you, clients, and bots improve' })).toBeInTheDocument();
    expect(screen.getByText('AI companies')).toBeInTheDocument();
    expect(screen.getByText('Human trust')).toBeInTheDocument();
    expect(screen.getByText('Music video')).toBeInTheDocument();
    expect(screen.getByText('Kids learning video')).toBeInTheDocument();
    expect(screen.getByText('College course')).toBeInTheDocument();
    expect(screen.getByText('Video game')).toBeInTheDocument();
    expect(screen.getByText('Simulation')).toBeInTheDocument();
    expect(screen.getByText('Photo and image editor')).toBeInTheDocument();
    expect(screen.getByText('Design and brand studio')).toBeInTheDocument();
    expect(screen.getByText('Documents and presentations')).toBeInTheDocument();
    expect(screen.getByText('Data dashboard')).toBeInTheDocument();
    expect(screen.getByText('Automation workflow')).toBeInTheDocument();
    expect(screen.getByText('3D or AR experience')).toBeInTheDocument();
    expect(screen.getByText('Audio and voice project')).toBeInTheDocument();
    expect(screen.getByText('Research and writing')).toBeInTheDocument();
    expect(screen.getByText('Voice and image consent rules')).toBeInTheDocument();
    expect(screen.getByText(/No fake testimonials/)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'What Buddy needs to beat ordinary vibe coding' })).toBeInTheDocument();
    expect(screen.getByText('Live preview while building')).toBeInTheDocument();
    expect(screen.getByText('One-click deploy')).toBeInTheDocument();
    expect(screen.getByText('Image-to-app and screenshot-to-dashboard')).toBeInTheDocument();
    expect(screen.getByText('Eval/test loop after every generated change')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Trust-first AI company builder roadmap' })).toBeInTheDocument();
    expect(screen.getByText('Win the trust lane first')).toBeInTheDocument();
    expect(screen.getByText('Ship one-prompt build packets')).toBeInTheDocument();
    expect(screen.getByText('Own bot businesses, not just apps')).toBeInTheDocument();
    expect(screen.getByText('Bundle essential business services')).toBeInTheDocument();
    expect(screen.getByText('Builder lanes')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '🤝 Buddy capability tracker' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '🧪 Buddy and bot test catalog' })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Buddy all-bot connection proof')).toBeInTheDocument());
    expect(screen.getByText('Actions-testable')).toBeInTheDocument();
    expect(screen.getByText('Resources per bot')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Always-clean PR, issue, and code-quality steward' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Fix why connected Stripe is making no money' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Sellable debugging system for apps, bots, workflows, and AI builds' })).toBeInTheDocument();
    expect(screen.getByText('AI App Debug Desk')).toBeInTheDocument();
    expect(screen.getByText('Debug every Actions and Agents failure')).toBeInTheDocument();
    expect(screen.getByText('Failure routing playbook')).toBeInTheDocument();
    expect(screen.getByText('Perfect-debug gates')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '💾 Future-proof bot memory' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '🔎 GitHub PR, issue, and comment triage' })).toBeInTheDocument();
    expect(screen.getByText('Buddy help for every pull request')).toBeInTheDocument();
    expect(screen.getByText('Retest')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Generated libraries' })).toBeInTheDocument();
    expect(screen.getByText('Sandbox bootcamp generator')).toBeInTheDocument();
    expect(screen.getByText('World Class Bot Building Sandbox Bootcamp')).toBeInTheDocument();
    expect(screen.getAllByText('Custom APIs').length).toBeGreaterThan(0);
    expect(screen.getAllByText('API bootcamps').length).toBeGreaterThan(0);
    expect(screen.getByText('Workflow generators')).toBeInTheDocument();
    expect(screen.getByText('Training tracks')).toBeInTheDocument();
    expect(screen.getByText('Resource seeds')).toBeInTheDocument();
    expect(screen.getByText('100 AI practice seeds')).toBeInTheDocument();
    expect(screen.getByText('Actions monitor panel')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Source: live')).toBeInTheDocument());
    expect(screen.getAllByText('1,248').length).toBeGreaterThan(0);
    expect(screen.getByText('8,736')).toBeInTheDocument();
  }, 15000);

  it('shows Buddy productivity tracking for owner, clients, and bots', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    await waitFor(() => expect(screen.getByText('Buddy Productivity Tracker')).toBeInTheDocument());
    expect(screen.getAllByText('For you').length).toBeGreaterThan(0);
    expect(screen.getByText('For clients')).toBeInTheDocument();
    expect(screen.getByText('For bots')).toBeInTheDocument();
    expect(screen.getByText('Learning loops Buddy watches')).toBeInTheDocument();
    expect(screen.getByText('Capability inventory loop')).toBeInTheDocument();
    expect(screen.getByText('Bot learning coverage')).toBeInTheDocument();
    expect(screen.getByText('$233')).toBeInTheDocument();
  });

  it('shows Buddy capability readiness and implementation blockers', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    await waitFor(() => expect(screen.getAllByText(/live ·/).length).toBeGreaterThanOrEqual(2));
    expect(screen.getByText('Built + test-covered')).toBeInTheDocument();
    expect(screen.getByText('Contract-ready')).toBeInTheDocument();
    expect(screen.getByText('Needs implementation before testing')).toBeInTheDocument();
    expect(screen.getByText('Path to fully coded')).toBeInTheDocument();
    expect(screen.getAllByText('Buddy test evidence dossier').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Sandbox command').length).toBeGreaterThan(0);
    expect(screen.getByText('All bots have a path')).toBeInTheDocument();
    expect(screen.getByText('Review placeholders')).toBeInTheDocument();
    expect(screen.getByText('Add direct tests')).toBeInTheDocument();
    expect(screen.getByText('Production readiness')).toBeInTheDocument();
    expect(screen.getByText('Final live-action approval gate')).toBeInTheDocument();
    expect(screen.getByText('Required owner phrase')).toBeInTheDocument();
    expect(screen.getByText('Sandbox candidates')).toBeInTheDocument();
    expect(screen.getByText('Buddy, help me make money with this bot. I approve the listed live actions and understand the risks.')).toBeInTheDocument();
    expect(screen.getByText('Review gates active')).toBeInTheDocument();
    expect(screen.getAllByText('Production ready').length).toBeGreaterThan(0);
    expect(screen.getByText('Approval needed')).toBeInTheDocument();
    expect(screen.getByText('Payment AutoCollector')).toBeInTheDocument();
    expect(screen.getByText('Buddy Core')).toBeInTheDocument();
  });

  it('shows bot capabilities and prepares sandbox test packets', async () => {
    const onBotTestRequest = vi.fn();
    render(
      <ActionsPage
        ActionsMonitorComponent={StubActionsMonitor}
        onBotTestRequest={onBotTestRequest}
      />,
    );

    await waitFor(() => expect(screen.getAllByText('Buddy Bot').length).toBeGreaterThan(0));
    expect(screen.getAllByText('For you').length).toBeGreaterThan(0);
    expect(screen.getByText('For your users')).toBeInTheDocument();
    expect(screen.getByText('For Buddy')).toBeInTheDocument();
    expect(screen.getByText('Code generation')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Find a bot'), { target: { value: 'lead' } });
    fireEvent.click(screen.getByRole('button', { name: /Lead Generation Bot/ }));
    expect(screen.getByRole('heading', { name: '🤖 Lead Generation Bot' })).toBeInTheDocument();
    expect(screen.getByText('Prospect scoring')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Test selected bot' }));
    expect(onBotTestRequest).toHaveBeenCalledWith(
      expect.objectContaining({
        slug: 'lead-gen-bot',
        mode: 'sandbox_only',
        approval: 'buddy_money_help_approval_required_before_live_actions',
      }),
    );
    expect(screen.getByRole('status')).toHaveTextContent('Sandbox test packet prepared for Lead Generation Bot');
    expect(screen.getByText(/Live money, outreach, and production actions stay blocked/)).toBeInTheDocument();
  });

  it('shows GitHub PR, issue, comment, and workflow triage', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    await waitFor(() => expect(screen.getByText('Repository Cleanroom')).toBeInTheDocument());
    expect(screen.getByText('Safe code quality gates')).toBeInTheDocument();
    expect(screen.getByText('Cleanup policy')).toBeInTheDocument();
    expect(screen.getByText('Ready PRs')).toBeInTheDocument();
    expect(screen.getByText('Failed gates')).toBeInTheDocument();
    expect(screen.getAllByText('Json Parse').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Python Syntax').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Javascript Syntax').length).toBeGreaterThan(0);
    expect(screen.getByText('Owner Approval For Close Or Merge')).toBeInTheDocument();
    await waitFor(() => expect(screen.getAllByText('Open PRs').length).toBeGreaterThan(0));
    expect(screen.getByText('Issue comments')).toBeInTheDocument();
    expect(screen.getByText('Review comments')).toBeInTheDocument();
    expect(screen.getByText('Restart queue')).toBeInTheDocument();
    expect(screen.getByText('Failed pull request rescue')).toBeInTheDocument();
    expect(screen.getByText('Active failed PR help queue')).toBeInTheDocument();
    expect(screen.getByText('Find blocker')).toBeInTheDocument();
    expect(screen.getByText('Retest proof')).toBeInTheDocument();
    expect(screen.getByText(/Buddy rescue: rebase or retest/)).toBeInTheDocument();
    expect(screen.getByText('Past failure rebuild backlog')).toBeInTheDocument();
    expect(screen.getByText('Replay')).toBeInTheDocument();
    expect(screen.getByText('Close loop')).toBeInTheDocument();
    expect(screen.getByText('Past PR failure')).toBeInTheDocument();
    expect(screen.getByText('Past workflow failure')).toBeInTheDocument();
    expect(screen.getAllByText('Past revenue blocker').length).toBeGreaterThan(0);
    expect(screen.getByText('PR restart and retest queue')).toBeInTheDocument();
    expect(screen.getAllByText(/Finish Buddy readiness tracker/).length).toBeGreaterThan(0);
    expect(screen.getByText('Workflow failures to retest')).toBeInTheDocument();
    expect(screen.getAllByText('System and Bot Builds Monitoring').length).toBeGreaterThan(0);
    expect(screen.getByText('workflow log capture and targeted rerun')).toBeInTheDocument();
    expect(screen.getByText(/Inspect failed job logs/)).toBeInTheDocument();
    expect(screen.getByText('Revenue blockers')).toBeInTheDocument();
    expect(screen.getAllByText(/No checkout-ready live Stripe offers/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Payment alert email recipients/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/GitHub payment notifications/).length).toBeGreaterThan(0);
    expect(screen.getByText('Rollover tiers')).toBeInTheDocument();
    expect(screen.getByText('Never one giant memory file')).toBeInTheDocument();
    expect(screen.getByText('Only useful data gets stored')).toBeInTheDocument();
    expect(screen.getByText('Required usefulness metadata')).toBeInTheDocument();
    expect(screen.getByText('Failure Summaries With Retest Commands')).toBeInTheDocument();
    expect(screen.getByText('Low Signal Chat Fillers')).toBeInTheDocument();
    expect(screen.getByText('Usefulness Reason')).toBeInTheDocument();
    expect(screen.getAllByText('System and Bot Builds Monitoring').length).toBeGreaterThan(0);
    expect(screen.getByText(/Workflow reruns require authenticated GitHub Actions permission/)).toBeInTheDocument();
  });

  it('prepares a sandboxed pull-request build packet', () => {
    const onBuildRequest = vi.fn();
    render(
      <ActionsPage
        ActionsMonitorComponent={StubActionsMonitor}
        onBuildRequest={onBuildRequest}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Prepare build packet' }));

    expect(onBuildRequest).toHaveBeenCalledWith(
      expect.objectContaining({
        builder: 'Full Bot System Builder',
        mode: 'sandbox_and_pull_request',
        approval: 'pull_request_required',
      }),
    );
    expect(screen.getByRole('status')).toHaveTextContent('sandbox-only');
  });

  it('switches builder and library lanes', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);
    await waitFor(() => expect(screen.getByRole('tab', { name: 'API Builder' })).toBeInTheDocument());

    fireEvent.click(screen.getByRole('tab', { name: 'API Builder' }));
    expect(screen.getByRole('heading', { name: '🔌 API Builder' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Webhooks Library/ }));
    expect(screen.getByText('Signed webhooks.')).toBeInTheDocument();
  });

  it('keeps security and sandbox controls visible', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    expect(screen.getByText('Webhook integrity')).toBeInTheDocument();
    expect(screen.getByText('Least privilege')).toBeInTheDocument();
    expect(screen.getByText('No payments, purchases, transfers, or ad spend')).toBeInTheDocument();
    expect(screen.getByText('Pull request and human review before deployment')).toBeInTheDocument();
  });

  it('opens and submits the Buddy operator console', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    fireEvent.click(screen.getByRole('button', { name: 'Open Buddy Live Console' }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Buddy command input'), {
      target: { value: 'build a new bot system' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Create Buddy Packet' }));
    await waitFor(() => expect(screen.getByText(/Packet buddy-op-test queued/)).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Close Buddy Command Center' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByText(/Build packet prepared for Full Bot System Builder/)).toBeInTheDocument();
  });
});
