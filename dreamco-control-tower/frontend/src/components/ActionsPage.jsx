import { useEffect, useMemo, useState } from 'react';
import ActionsMonitor from './ActionsMonitor.jsx';
import BuddyCommandCenter from './BuddyCommandCenter.jsx';

const FALLBACK_BUILDERS = [
  { id: 'full-bot-system', name: 'Full Bot System Builder', icon: '🤖', outputs: ['profile', 'blueprint', 'tool', 'api', 'webhook', 'workflow', 'skill', 'sandbox', 'tests'], approval: 'pull_request_required' },
  { id: 'tools-builder', name: 'Tool Builder', icon: '🔧', outputs: ['tool', 'schema', 'tests', 'documentation'], approval: 'pull_request_required' },
  { id: 'apis-builder', name: 'API Builder', icon: '🔌', outputs: ['api', 'schema', 'tests', 'documentation'], approval: 'pull_request_required' },
  { id: 'webhooks-builder', name: 'Webhook Builder', icon: '🪝', outputs: ['webhook', 'schema', 'tests', 'documentation'], approval: 'pull_request_required' },
  { id: 'workflows-builder', name: 'Workflow Builder', icon: '🔁', outputs: ['workflow', 'schema', 'tests', 'documentation'], approval: 'pull_request_required' },
  { id: 'skills-builder', name: 'Skill Builder', icon: '🧠', outputs: ['skill', 'schema', 'tests', 'documentation'], approval: 'pull_request_required' },
  { id: 'sandboxes-builder', name: 'Sandbox Builder', icon: '🧪', outputs: ['sandbox', 'schema', 'tests', 'documentation'], approval: 'pull_request_required' },
  { id: 'resources-builder', name: 'Resource Library Builder', icon: '📚', outputs: ['resource', 'schema', 'tests', 'documentation'], approval: 'pull_request_required' },
];

const FALLBACK_LIBRARIES = [
  { id: 'tools', name: 'Tools Library', icon: '🔧', count: 1248, description: 'Typed, permission-aware tools with tests and audit metadata.' },
  { id: 'apis', name: 'Apis Library', icon: '🔌', count: 1248, description: 'Versioned per-bot APIs with schemas, rate limits, and approval gates.' },
  { id: 'webhooks', name: 'Webhooks Library', icon: '🪝', count: 1248, description: 'Signed, idempotent per-bot event contracts with queued processing.' },
  { id: 'workflows', name: 'Workflows Library', icon: '🔁', count: 1248, description: 'Reusable validation and delivery workflows with least privilege.' },
  { id: 'skills', name: 'Skills Library', icon: '🧠', count: 1248, description: 'Versioned multi-step skills with evidence and tests.' },
  { id: 'sandboxes', name: 'Sandboxes Library', icon: '🧪', count: 1248, description: 'Isolated test environments with fixtures, limits, and no live money movement.' },
  { id: 'resources', name: 'Resources Library', icon: '📚', count: 1248, description: 'Per-bot starter kits with 100 curated resource slots and learning prompts.' },
];

const FALLBACK_BOOTCAMP_BASELINE = {
  name: 'World Class Bot Building Sandbox Bootcamp',
  audiences: ['owner', 'buddy', 'client'],
  sandbox_principles: [
    'hermetic_by_default',
    'deterministic_fixtures',
    'network_and_secrets_mocked',
    'api_contract_first',
    'workflow_generated_per_test',
    'human_approval_for_external_impact',
  ],
  module_count: 7,
  top_ai_company_resource_seed_count: 100,
  source_boundaries: [
    'public_documentation_only',
    'owner_approved_notes_only',
    'no_private_or_proprietary_company_material',
  ],
};

const FALLBACK_BUDDY_INVENTORY = {
  generated_at: null,
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
      profiled_from_existing_system_needs_direct_impl_check: 7,
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
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      description: 'Buddy routes coding, debugging, tool-building, orchestration, and safe sandbox testing across the bot fleet.',
      capabilities: ['Code generation', 'Cross-bot orchestration', 'Tool-building', 'Debugging', 'API integration builder', 'Sandbox testing'],
      tests: ['tests/test_buddy_bot.py'],
      test_count: 1,
      build_state: 'built_and_test_covered',
      test_state: 'ready_for_test_run',
      production_readiness_status: 'production_ready',
      risk_hint: 'standard',
    },
    {
      slug: 'buddy_core',
      name: 'Buddy Core',
      division: 'CommandCore',
      description: 'Core Buddy runtime for command routing, repository awareness, and supervised automation.',
      capabilities: ['Command routing', 'Repository scans', 'Build packet planning', 'Safety gates'],
      tests: [],
      test_count: 0,
      build_state: 'built_and_test_covered',
      test_state: 'ready_for_test_run',
    },
    {
      slug: 'buddy-tool-builder',
      name: 'Buddy Tool Library Builder Bot',
      division: 'DreamCodeLab',
      description: 'Builds reusable tool libraries, SDKs, APIs, and test scaffolds for Buddy and the fleet.',
      capabilities: ['SDK scaffolding', 'Tool library creation', 'API client generation', 'Documentation generation'],
      tests: [],
      test_count: 0,
      build_state: 'built_contract_ready',
      test_state: 'ready_for_contract_testing',
    },
  ],
  bots: [],
  attention: {
    needs_implementation: [
      { slug: 'ai_enablement_hub', name: 'AI Enablement Hub', division: 'DreamAIInfra' },
      { slug: 'auto_client_hunter', name: 'Auto Client Hunter', division: 'DreamSalesPro' },
      { slug: 'elite_scraper', name: 'Elite Scraper', division: 'DreamSalesPro' },
      { slug: 'god_mode_autocloser', name: 'God Mode AutoCloser', division: 'DreamSalesPro' },
      { slug: 'payment_autocollector', name: 'Payment AutoCollector', division: 'DreamFinance' },
    ],
  },
};

const FALLBACK_GITHUB_TRIAGE = {
  generated_at: null,
  repo: 'DreamCo-Technologies/Dreamcobots',
  summary: {
    open_prs: 0,
    open_issues: 0,
    issue_comments_scanned: 0,
    pr_review_comments_scanned: 0,
    workflow_runs_scanned: 0,
    failed_workflow_runs: 0,
    active_workflow_runs: 0,
    pr_restart_queue: 0,
  },
  pr_restart_queue: [],
  failed_workflow_runs: [],
  notes: ['Run the GitHub triage scan to populate live repository data.'],
};

const FALLBACK_REPOSITORY_STEWARDSHIP = {
  generated_at: null,
  repo: 'DreamCo-Technologies/Dreamcobots',
  summary: {
    open_prs: 0,
    open_issues: 0,
    ready_prs: 0,
    stale_prs: 0,
    stale_issues: 0,
    failed_workflow_runs: 0,
    restart_queue: 0,
    planned_close_prs: 0,
    planned_close_issues: 0,
    quality_checks: 3,
    failed_quality_checks: 0,
    skipped_quality_checks: 0,
    cleanroom_ready: false,
  },
  quality_checks: [
    { name: 'json_parse', status: 'pending', scanned: 0, failures: [] },
    { name: 'python_syntax', status: 'pending', scanned: 0, failures: [] },
    { name: 'javascript_syntax', status: 'pending', scanned: 0, failures: [] },
  ],
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
};

const FALLBACK_BUDDY_PRODUCTIVITY = {
  generated_at: null,
  summary: {
    productivity_score: 0,
    bot_count: 0,
    runtime_ready_bots: 0,
    production_ready_bots: 0,
    approval_gated_bots: 0,
    open_prs: 0,
    open_issues: 0,
    failed_workflow_runs: 0,
    failed_quality_checks: 0,
    estimated_monthly_savings_usd: 0,
    tracked_learning_loops: 0,
  },
  owner_productivity: { tracks: [], current_focus: [] },
  client_productivity: { tracks: [], ready_to_show: [] },
  bot_productivity: { tracks: [], coverage: {} },
  learning_loops: [],
  next_actions: [],
};

const FALLBACK_RELEASE_READINESS = {
  generated_at: null,
  branch: 'codex/bot-test-dashboard',
  mission: 'Make DreamCo reliable, demonstrable, and evidence-backed.',
  summary: {
    release_readiness_score: 0,
    first_ten_complete: 0,
    first_ten_active: 10,
    first_ten_blocked: 0,
    top_100_groups_complete: 0,
    top_100_groups_active: 6,
    top_100_groups_blocked: 0,
    open_prs: 58,
    open_issues: 17,
    failed_workflow_runs: 31,
    failed_quality_checks: 0,
    production_ready_bots: 101,
    bot_profiles_scanned: 1051,
    storage_ready: true,
    revenue_rescue_ready: false,
  },
  first_ten_updates: [
    { id: 'correct_registry_and_readme_counts', title: 'Correct registry and README counts', status: 'complete', proof: [], missing: [], next: 'Keep claims tied to evidence.' },
    { id: 'classify_all_profiles_by_implementation_status', title: 'Classify all profiles by implementation status', status: 'active', proof: [], missing: [], next: 'Normalize every bot with runtime and test proof.' },
    { id: 'triage_open_pull_requests', title: 'Triage open pull requests', status: 'active', proof: [], missing: [], next: 'Sort PRs into merge, rebuild, replace, duplicate, and close queues.' },
  ],
  top_100_groups: [
    { id: 'repository_stability', title: 'Repository Stability', planned_updates: 20, status: 'active', metrics: {}, focus: [], first_move: 'Make one required CI workflow and classify open PRs.', next: 'Reduce stale PRs and failed workflow runs.' },
    { id: 'bot_truth_registry', title: 'Bot Truth Registry', planned_updates: 20, status: 'active', metrics: {}, focus: [], first_move: 'Generate public catalog only from the master registry.', next: 'Prove each bot with runtime and tests.' },
    { id: 'trustworthy_autonomy', title: 'Trustworthy Autonomy', planned_updates: 15, status: 'active', metrics: {}, focus: [], first_move: 'Enforce autonomy policies as code.', next: 'Connect approvals to runtime gates.' },
  ],
  already_done: [],
  currently_building: [],
  blocked_or_unproven: [],
  next_actions: ['Run npm run report:release-readiness to populate live comparison data.'],
};

const FALLBACK_STORAGE_GUARD = {
  generated_at: null,
  summary: {
    storage_ready: true,
    checks: 0,
    failed_checks: 0,
    warnings: 0,
    memory_tiers: 4,
    partitioning_rules: 7,
    compaction_rules: 6,
    useful_keep_categories: 10,
    useful_drop_categories: 10,
    useful_required_metadata: 8,
    approval_gates: 11,
    largest_resource_shard_mb: 0,
    largest_resource_shard: 'generated fallback',
    resource_shard_count: 45,
    bot_resource_entries_checked: 0,
  },
  budgets: {
    generated_index_max_mb: 10,
    generated_library_max_mb: 25,
    generated_resource_shard_max_mb: 25,
    single_memory_record_max_kb: 256,
    single_bot_hot_partition_max_mb: 128,
    single_bot_warm_partition_max_mb: 256,
    single_archive_max_mb: 512,
    dashboard_report_max_mb: 5,
  },
  useful_data_policy: {
    rule: 'Only store data that can improve owner decisions, client delivery, bot learning, debugging, compliance, or reproducible rebuilds.',
    keep_categories: [
      'approved_user_preferences',
      'active_task_context',
      'tested_skill_lessons',
      'failure_summaries_with_retest_commands',
      'build_rebuild_and_debug_packets',
    ],
    drop_categories: [
      'duplicate_records',
      'raw_scratchpads_after_summary',
      'stale_logs_without_failures_or_decisions',
      'secrets_tokens_or_api_keys',
      'low_signal_chat_fillers',
    ],
    required_metadata: ['source', 'owner_or_bot', 'usefulness_reason', 'retention_tier', 'dedupe_key', 'redaction_state'],
    minimum_usefulness_score_to_store: 3,
  },
  memory_tiers: [
    { tier: 'hot', purpose: 'Active task memory and recent bot context.', rollover_at_mb: 128 },
    { tier: 'warm', purpose: 'Approved lessons, summaries, and reusable skill memory.', rollover_at_mb: 256 },
    { tier: 'cold', purpose: 'Compressed audit archives and long-term evidence.', rollover_at_mb: 512 },
    { tier: 'vector', purpose: 'Searchable memory references with partitioned vectors.', rollover_at_mb: 256 },
  ],
  partitioning_rules: [
    'Never store all bot resources, memories, events, vectors, or source snapshots in one monolithic file.',
    'Every large collection must have a small manifest index and independently loadable shards.',
    'Keep dashboards on summaries and manifests so the UI can load without reading the full memory corpus.',
  ],
  compaction_rules: [],
  checks: [],
  warnings: [],
};

const FALLBACK_APP_FOUNDRY = {
  generated_at: null,
  mission: 'Make DreamCo the in-house A-to-Z foundry for building, testing, packaging, hosting, and deploying games, websites, apps, school courses, simulations, dashboards, creative media, and business bot systems.',
  ownership_rule: 'DreamCo-owned repository code is the source of truth. External hosts and services are deployment targets or adapters, not the builder of record.',
  operating_posture: 'sandbox_first_pull_request_review',
  summary: {
    readiness_score: 0,
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
    { id: 'games', label: 'Games', description: 'Prompt-to-playable prototypes with design docs, levels, scoring, controls, saves, and test scenes.', outputs: ['game design doc', 'playable prototype', 'test plan'], host_targets: ['github_pages', 'static_host'], approval_gates: ['asset rights'], status: 'ready_for_sandbox_preview' },
    { id: 'websites', label: 'Websites', description: 'Client-ready websites, landing pages, portals, documentation hubs, and product showcases.', outputs: ['site map', 'responsive UI', 'deployment bundle'], host_targets: ['github_pages', 'hostinger'], approval_gates: ['brand claim review'], status: 'ready_for_sandbox_preview' },
    { id: 'apps', label: 'Apps', description: 'Full app builds with screens, local-first data, API adapters, tests, and rollback notes.', outputs: ['product spec', 'data model', 'test suite'], host_targets: ['local_laptop', 'managed_node_host'], approval_gates: ['credential approval'], status: 'ready_for_sandbox_preview' },
    { id: 'school_courses', label: 'School courses', description: 'Age-appropriate course generators for lessons, quizzes, rubrics, teacher notes, and student-safe media plans.', outputs: ['course outline', 'lesson modules', 'quizzes'], host_targets: ['github_pages', 'course_export'], approval_gates: ['minor safety'], status: 'ready_for_sandbox_preview' },
    { id: 'simulations', label: 'Simulations', description: 'Business, science, finance, operations, robotics, real estate, and training simulations with adjustable variables.', outputs: ['scenario model', 'simulation engine', 'results dashboard'], host_targets: ['github_pages', 'container_host'], approval_gates: ['no guaranteed outcome claims'], status: 'ready_for_sandbox_preview' },
    { id: 'dashboards', label: 'Dashboards', description: 'Operational command centers, prospectus pages, bot dashboards, KPI trackers, and client demo rooms.', outputs: ['metric catalog', 'status cards', 'alert rules'], host_targets: ['github_pages', 'hostinger'], approval_gates: ['private data redaction'], status: 'ready_for_sandbox_preview' },
    { id: 'creative_media', label: 'Creative media', description: 'Music video packets, image editing workflows, brand kits, storyboards, audio plans, and asset-rights ledgers.', outputs: ['concept', 'storyboard', 'rights log'], host_targets: ['static_preview', 'client_handoff_packet'], approval_gates: ['written consent'], status: 'ready_for_sandbox_preview' },
    { id: 'business_bots', label: 'Business bots', description: 'Client business workers for sales, support, booking, estimating, CRM updates, lead capture, and delivery workflows.', outputs: ['bot prospectus', 'tool contracts', 'approval packet'], host_targets: ['local_laptop', 'managed_node_host'], approval_gates: ['money movement approval'], status: 'ready_for_sandbox_preview' },
  ],
  in_house_systems: ['prompt_to_plan', 'template_generator', 'sandbox_bootcamp_generator', 'api_builder', 'webhook_builder', 'deployment_packager', 'rollback_checkpoint_manager', 'client_prospectus_generator'],
  deployment_targets: [
    { id: 'github_pages', label: 'GitHub Pages', role: 'Free static previews for dashboards, websites, courses, simple games, and static simulations.', status: 'ready_for_static_frontend' },
    { id: 'hostinger', label: 'Hostinger', role: 'Starter public hosting target for Buddy dashboard builds and client demos.', status: 'configured_adapter' },
    { id: 'local_laptop', label: 'Local laptop', role: 'Development, demos, sandbox runs, and owner-supervised builds before public deployment.', status: 'ready' },
    { id: 'managed_node_host', label: 'Managed Node host', role: 'Node or API-backed apps after secrets and rollback gates are configured.', status: 'planned_adapter' },
  ],
  quality_gates: ['all_generated_code_builds', 'sandbox_test_packet_exists', 'no_secrets_committed', 'owner_approval_before_live_money_outreach_or_deploy'],
  next_build_targets: ['Create one prompt-to-preview wizard for all eight lanes.'],
  gaps: ['Production backend hosting needs owner-approved credentials and secrets before live apps.'],
};

const FALLBACK_BOT_FOUNDER_APP_STORE = {
  generated_at: null,
  mission: 'Every DreamCo bot studies its market, designs a useful autonomous app, prepares a safe company plan, and packages itself for the DreamCo app store.',
  positioning: 'Each bot is treated as a supervised business owner preparing a revolutionary app, website, workflow, simulation, course, or service for a DreamCo-owned app store.',
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
    { id: 'competition_lab', label: 'Competition Lab', purpose: 'Study public competitors, substitutes, pricing, feature gaps, positioning, reviews, and customer complaints.', outputs: ['competitor_map', 'feature_gap_matrix', 'pricing_notes'] },
    { id: 'autonomous_money_lab', label: 'Autonomous Money Lab', purpose: 'Find ethical value creation, offer packaging, pricing tests, cost savings, and revenue recovery ideas.', outputs: ['revenue_model', 'offer_stack', 'risk_disclosures'] },
    { id: 'app_builder_lab', label: 'App Builder Lab', purpose: 'Design one app-store-ready product with user, workflow, demo, sandbox test, and deployment plan.', outputs: ['app_concept', 'mvp_scope', 'deployment_plan'] },
    { id: 'marketing_lab', label: 'Marketing Lab', purpose: 'Draft ethical advertising, content, SEO, demos, launch copy, and campaign experiments for owner review.', outputs: ['audience_segments', 'ad_drafts', 'launch_checklist'] },
  ],
  app_store_categories: [
    { category: 'business_automation', bot_count: 185 },
    { category: 'developer_tools', bot_count: 152 },
    { category: 'finance_and_payments', bot_count: 120 },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      emoji: '🤝',
      division: 'CommandCore',
      app_store_category: 'business_automation',
      target_customer: 'DreamCo owners and client teams',
      autonomous_app_concept: { name: 'Buddy Bot App', promise: 'A supervised command center for safe AI company building.' },
      app_store_listing: { status: 'draft_ready_for_owner_review' },
    },
  ],
  approval_gates: ['customer_outreach', 'ad_spend', 'public_deployment', 'payment_collection', 'money_movement', 'app_store_publish'],
};

const FALLBACK_24_HOUR_SCALING = {
  generated_at: null,
  mission: 'Keep DreamCo improving around the clock through safe 24-hour research, build, test, app-store, and approval cycles while keeping paid cloud and GitHub usage as low as possible.',
  default_mode: 'continuous_supervised_cheap_ops',
  summary: {
    readiness_score: 0,
    cycles_defined: 6,
    safe_automation_steps: 24,
    cycle_approval_steps: 28,
    always_blocked_gates: 11,
    scale_lanes: 12,
    bot_founder_packets: 1248,
    app_store_categories: 12,
    app_foundry_lanes: 8,
    storage_ready: true,
    min_replicas: 0,
    max_replicas: 1,
    self_healing_enabled: true,
    cheap_24_hour_mode: true,
    idle_sleep_enabled: true,
    max_one_instance: true,
    cloud_run_cpu_throttling: true,
    github_actions_default: 'manual_or_path_gated',
    free_first_ai_routing: true,
    github_cost_guardrails: 5,
    ai_cost_guardrails: 5,
    codex_style_capabilities: 8,
  },
  daily_cycles: [
    { id: 'market_research_cycle', window: '00:00-03:00', purpose: 'Study competitors, app-store ideas, customer problems, pricing, reviews, and market gaps.', safe_automation: ['public_source_queue', 'competitor_notes'], approval_required: ['customer_contact'] },
    { id: 'build_cycle', window: '03:00-07:00', purpose: 'Turn top opportunities into app concepts, code plans, sandbox prototypes, and pull-request-safe tasks.', safe_automation: ['app_concept_generation', 'mvp_scope'], approval_required: ['production_deploy'] },
    { id: 'test_cycle', window: '07:00-11:00', purpose: 'Run syntax checks, smoke tests, API sandbox tests, workflow generators, and dashboard health checks.', safe_automation: ['sandbox_tests', 'report_refresh'], approval_required: ['live_api_mutation'] },
    { id: 'package_cycle', window: '11:00-15:00', purpose: 'Package app-store listings, prospectus pages, demo scripts, mockups, and pricing drafts.', safe_automation: ['listing_drafts', 'pricing_options'], approval_required: ['public_publish'] },
    { id: 'growth_cycle', window: '15:00-19:00', purpose: 'Prepare ethical marketing, customer discovery, launch experiments, SEO briefs, and outreach drafts.', safe_automation: ['content_drafts', 'lead_scoring'], approval_required: ['ad_spend'] },
    { id: 'review_cycle', window: '19:00-24:00', purpose: 'Summarize what worked, what failed, what needs approval, and what should ship next.', safe_automation: ['daily_scorecard', 'approval_queue'], approval_required: ['merge'] },
  ],
  scale_lanes: ['bot_founder_packets', 'app_store_listing_drafts', 'sandbox_bootcamps', 'competitor_research', 'customer_discovery', 'marketing_drafts'],
  always_blocked_without_owner_approval: ['customer_outreach', 'ad_spend', 'money_movement', 'public_deployment', 'app_store_publish', 'credential_change'],
  next_actions: ['Connect this report to a scheduled workflow when recurring automation is approved.'],
};

const FALLBACK_BUDDY_CODEX_CHEAP_OPS = {
  generated_at: null,
  mission: 'Make Buddy a governed Codex-style coding, debugging, orchestration, and operations teammate while keeping DreamCo free or cheap by default.',
  summary: {
    codex_style_capabilities: 6,
    bot_count: 1248,
    bots_connected_to_buddy: 1248,
    cheap_24_hour_mode: true,
    min_replicas: 0,
    max_replicas: 1,
    github_cost_guardrails: 5,
    ai_cost_guardrails: 5,
    low_cost_ai_resources: 86,
    gemini_resources: 8,
    owner_approval_boundaries: 12,
    aggressive_mode_available: true,
    aggressive_mode_runs: 8,
    aggressive_mode_hard_limits: 7,
    unlimited_autonomy_claimed: false,
    billing_bypass_claimed: false,
  },
  always_on_strategy: {
    mode: '24_hour_supervised_queue_not_24_hour_paid_compute',
    plain_english: 'Buddy keeps the system moving by rotating cheap local/report-based cycles and queued work packets. Bots do not need expensive always-on cloud containers to stay useful.',
    runtime_layers: ['static dashboard and generated reports', 'local scripts on owner laptop', 'manual or path-gated GitHub Actions', 'Cloud Run request-based service that sleeps when idle', 'free or low-cost AI model routes'],
  },
  aggressive_mode_contract: {
    button_label: 'Aggressive Mode',
    endpoint: '/api/buddy-ops/aggressive-mode',
    default_state: 'owner_triggered_only',
    duration_hours: 24,
    execution_mode: 'supervised_repository_wide_queue',
    intensity: 'maximum_safe_local_and_report_generation',
    what_it_runs: [
      'refresh every generated report',
      'scan every bot registry and connection report',
      'queue every bot for sandbox-first test or rebuild packets',
      'run local syntax and smoke checks before GitHub Actions',
      'run GitHub cost saver and repository stewardship scans',
      'refresh AI model routing and Gemini low-cost paths',
      'prepare pull-request packets for failures',
      'summarize approval gates and next best actions',
    ],
    hard_limits: [
      'no paid always-on AI loop',
      'no customer outreach',
      'no ad spend',
      'no money movement',
      'no credential changes',
      'no destructive repository action',
      'no production deployment without explicit owner approval',
    ],
  },
  codex_style_capabilities: [
    { id: 'repo_reader', label: 'Repository reader', buddy_can: 'Scan files, reports, bot profiles, configs, tests, workflows, and dashboards.', cheap_path: 'Use local file reads and generated JSON reports before network calls.', approval: 'No approval for read-only local scans.' },
    { id: 'code_editor', label: 'Code editor', buddy_can: 'Draft scoped code, config, test, and documentation changes for review.', cheap_path: 'Use deterministic templates and smallest-capable AI routes before premium models.', approval: 'Owner approval before push, merge, deploy, or destructive edits.' },
    { id: 'test_runner', label: 'Test and debug runner', buddy_can: 'Run syntax checks, unit tests, smoke tests, report freshness checks, and failure triage.', cheap_path: 'Run locally first; use GitHub Actions only for release evidence or remote-only checks.', approval: 'Owner approval before increasing scheduled CI frequency or paid runner usage.' },
    { id: 'pr_helper', label: 'Pull request helper', buddy_can: 'Prepare PR summaries, compare goals to repository proof, and queue fixes for failed checks.', cheap_path: 'Use cached GitHub triage reports and local diffs before API refreshes.', approval: 'Owner approval before closing, merging, rebasing, or force-pushing PR branches.' },
    { id: 'model_router', label: 'AI model router', buddy_can: 'Pick local/static/free/cheap/premium model routes based on task risk and quality needs.', cheap_path: 'Prefer local reports, cache, Gemini low-cost routes, and small models for drafts.', approval: 'Owner approval before paid always-on loops, premium batches, or production customer data.' },
    { id: 'bot_orchestrator', label: 'Bot orchestrator', buddy_can: 'Create supervised work packets for every bot so the fleet keeps learning, testing, and packaging.', cheap_path: 'Queue work packets and summaries instead of running every bot as a paid live service.', approval: 'Owner approval before customer outreach, money movement, deploys, or account changes.' },
  ],
  github_free_cheap_plan: {
    default_hosting: 'GitHub Pages for static dashboards and docs when possible.',
    actions_policy: 'Manual, path-gated, short retention, local-first.',
  },
  cheap_ai_resource_plan: {
    default_mode: 'free_or_low_cost_first',
    local_first: true,
    cache_first: true,
    secret_name: 'GOOGLE_API_KEY',
  },
  approval_boundaries: ['money_movement', 'credential_change', 'paid_github_minutes_increase', 'paid_ai_always_on_loop'],
};

const FALLBACK_SPECIALIZED_BOT_KNOWLEDGE = {
  generated_at: null,
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
    { id: 'customer_intelligence', label: 'Customer Intelligence', purpose: 'Know who the bot helps, what problem they have, what proof they need, and what outcome they care about.' },
    { id: 'competitor_intelligence', label: 'Competitor Intelligence', purpose: 'Study public competitors, substitutes, pricing, feature gaps, reviews, positioning, onboarding, and trust signals.' },
    { id: 'app_builder_knowledge', label: 'App Builder Knowledge', purpose: 'Know how to turn the bot into a usable app, website, course, game, simulation, dashboard, or workflow.' },
    { id: 'safety_and_approval', label: 'Safety and Approval', purpose: 'Know what it may draft versus what requires owner approval before customer, money, deployment, or account impact.' },
  ],
  source_policy: {
    allowed: ['public documentation', 'public pricing pages', 'public reviews', 'owner-approved notes', 'generated sandbox evidence', 'test reports'],
    blocked: ['secrets', 'private account data without approval', 'copied proprietary code', 'low-signal raw scratchpads'],
  },
  memory_tiers: [
    { id: 'hot', purpose: 'Active task context and short-lived work notes.' },
    { id: 'warm', purpose: 'Approved lessons, competitor summaries, and reusable workflows.' },
    { id: 'cold', purpose: 'Long-term audit evidence and archived experiments.' },
    { id: 'vector', purpose: 'Search references partitioned by division, bot, domain, and month.' },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      emoji: '🤝',
      division: 'CommandCore',
      target_customer: 'DreamCo owners and client teams',
      app_concept_name: 'Buddy Bot App',
      dashboard_status: 'ready_for_specialized_learning',
      specialized_study_queue: ['Map customer pains, buying triggers, and proof needs.', 'Compare public competitors and substitute workflows.'],
    },
  ],
  approval_gates: ['customer_outreach', 'ad_spend', 'money_movement', 'public_deployment', 'app_store_publish'],
};

const FALLBACK_AI_AGENT_MODEL_LIBRARY = {
  generated_at: null,
  mission: 'Give Buddy a governed prompt, tool, agent, and model-resource library so every bot can pick the best AI route for each task, explain tradeoffs, and fall back safely.',
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
      good_at: ['complex planning', 'code repair', 'tool calling', 'multimodal app building'],
      bad_at: ['unverified current facts without retrieval', 'tasks needing disabled credentials'],
      best_tasks: ['architecture', 'coding', 'debugging', 'model_evaluation'],
      status: 'candidate_verify_model_id_before_production',
    },
    {
      id: 'google_gemini__quality',
      provider: 'Google',
      label: 'Gemini multimodal and long context - Best Quality',
      tier: 'quality',
      good_at: ['large context', 'document/video understanding', 'research synthesis'],
      bad_at: ['private docs without privacy review'],
      best_tasks: ['market_research', 'video_storyboard', 'course_building'],
      status: 'candidate_verify_model_id_before_production',
    },
  ],
  task_routes: [
    { task_type: 'coding', primary_resource: 'openai_reasoning__quality', fallback_resources: ['deepseek_coder_reasoner__quality', 'qwen_models__quality'], required_evals: ['task_success', 'cost_latency', 'safety_gate'] },
    { task_type: 'image_generation', primary_resource: 'openai_image__quality', fallback_resources: ['black_forest_image__quality', 'stability_image__quality'], required_evals: ['task_success', 'source_quality', 'safety_gate'] },
    { task_type: 'market_research', primary_resource: 'perplexity_search__quality', fallback_resources: ['google_gemini__quality', 'openai_reasoning__quality'], required_evals: ['source_quality', 'user_value', 'safety_gate'] },
  ],
  agent_prompt_tool_matrix: [
    { agent_type: 'coding_agent', label: 'Coding Agent', prompt_types: ['task_brief', 'tool_contract', 'code_review', 'test_generation'], tool_types: ['file_reader', 'code_editor', 'test_runner', 'api_client'], best_for: ['app code', 'tests', 'refactors'], avoid_for: ['large rewrites without tests'] },
    { agent_type: 'creative_studio_agent', label: 'Creative Studio Agent', prompt_types: ['task_brief', 'visual_prompt', 'voice_consent'], tool_types: ['image_generator', 'image_editor', 'video_generator'], best_for: ['image', 'video', 'music', 'storyboards'], avoid_for: ['unapproved likeness cloning'] },
    { agent_type: 'model_router_agent', label: 'Model Router Agent', prompt_types: ['task_brief', 'structured_output', 'rubric_eval'], tool_types: ['vector_search', 'reranker', 'approval_gate'], best_for: ['model selection', 'fallbacks', 'cost-quality tradeoffs'], avoid_for: ['using disabled providers'] },
  ],
};

const FALLBACK_BUSINESS_LAUNCH_EXPANSION = {
  generated_at: null,
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
    client_must_approve: ['sub_agent_creation', 'domain_purchase', 'business_registration_filing', 'app_store_submission', 'paid_ad_spend', 'customer_or_supplier_outreach'],
    blocked_without_professional_review: ['legal_filing_as_attorney', 'tax_advice_as_accountant', 'guaranteed_profit_claim'],
  },
  service_lanes: [
    { id: 'business_formation', label: 'Business Formation', purpose: 'Prepare business name checks, entity comparison notes, registration checklist, permits checklist, tax/accounting handoff, and launch timeline.', deliverables: ['entity_options_brief', 'registration_checklist', 'permit_research'], approval_gates: ['business_registration_filing'] },
    { id: 'domains_and_brand', label: 'Domains and Brand', purpose: 'Find domain options, social handles, naming risks, brand kit, logo direction, and website launch plan.', deliverables: ['domain_shortlist', 'brand_brief', 'website_launch_plan'], approval_gates: ['domain_purchase'] },
    { id: 'supplier_network', label: 'Supplier Network', purpose: 'Find supplier categories, prepare RFQ packets, compare terms, track reliability signals, and create approval-ready outreach drafts.', deliverables: ['supplier_shortlist', 'rfq_packet', 'terms_comparison'], approval_gates: ['customer_or_supplier_outreach'] },
    { id: 'logistics_and_supply_routes', label: 'Logistics and Supply Routes', purpose: 'Prepare trucking routes, pickup/dropoff planning, cost assumptions, delivery windows, route risk notes, and dispatch workflow drafts.', deliverables: ['route_plan', 'dispatch_workflow'], approval_gates: ['supplier_or_carrier_contact'] },
  ],
  sub_agent_roles: [
    { id: 'business_formation_agent', label: 'Business Formation Agent', can_prepare: ['name research', 'entity comparison notes'], cannot_do_without_approval: ['file registrations', 'give legal or tax advice'] },
    { id: 'domain_brand_agent', label: 'Domain and Brand Agent', can_prepare: ['domain shortlist', 'brand kit'], cannot_do_without_approval: ['buy domains', 'claim trademarks'] },
    { id: 'supplier_agent', label: 'Supplier Agent', can_prepare: ['supplier lists', 'RFQs'], cannot_do_without_approval: ['contact suppliers', 'sign terms'] },
  ],
};

const FALLBACK_BUDDY_COMMERCE_PUBLISHING = {
  generated_at: null,
  mission: 'Make Buddy the download-easy, task-manager-first commerce and publishing operator for domains, app builds, web publishing, app-store readiness, device installs, and safe autonomous money research.',
  positioning: 'Buddy captures goals, breaks them into tasks, assigns bots, tracks evidence, prepares domain and store packets, packages downloads, and searches public web opportunities without live money or account actions until approved.',
  default_mode: 'research_draft_package_test_then_owner_approval',
  summary: {
    readiness_score: 100,
    bot_count: 1248,
    commerce_lanes: 5,
    download_targets: 4,
    app_store_targets: 5,
    task_manager_layers: 10,
    app_categories: 40,
    approval_wall_gates: 11,
    safe_actions: 28,
    live_actions_blocked: 28,
    download_packets_ready: 2,
    store_packets_ready: 5,
    web_research_policy_ready: true,
    can_sell_domains_after_approval: true,
    can_prepare_app_store_submissions: true,
    can_prepare_device_downloads: true,
    can_research_autonomous_money: true,
  },
  commerce_lanes: [
    { id: 'domains', label: 'Domain Selling and Management', safe_actions: ['search domain ideas', 'compare public registrar pricing', 'draft domain shortlist'], approval_required: ['buy_domain', 'sell_domain', 'change_dns'], dashboard_status: 'ready_for_buddy_supervised_packet' },
    { id: 'app_self_publish', label: 'Self-Publishing Apps', safe_actions: ['build release checklist', 'draft privacy notes', 'prepare rollback checklist'], approval_required: ['submit_store_listing', 'publish_public_release'], dashboard_status: 'ready_for_buddy_supervised_packet' },
    { id: 'client_downloads', label: 'Easy Client Downloads', safe_actions: ['prepare web link', 'prepare PWA install instructions', 'track device support'], approval_required: ['ship_installer', 'submit_mobile_app'], dashboard_status: 'ready_for_buddy_supervised_packet' },
    { id: 'task_manager_chatbot', label: 'Task Manager Chatbot', safe_actions: ['capture goals', 'split tasks', 'assign bots', 'summarize blockers'], approval_required: ['create_external_task', 'send_notification'], dashboard_status: 'ready_for_buddy_supervised_packet' },
    { id: 'web_money_research', label: 'Autonomous Money Research', safe_actions: ['search public opportunities', 'draft offers', 'simulate pricing'], approval_required: ['contact_customer', 'run_ads', 'charge_payment'], dashboard_status: 'ready_for_buddy_supervised_packet' },
  ],
  download_targets: [
    { id: 'web_app', label: 'Web App', goal: 'Open Buddy from any browser with no install.', status: 'ready_for_static_preview' },
    { id: 'pwa_install', label: 'PWA Install', goal: 'Let clients add Buddy to phone or desktop home screens from the web version.', status: 'ready_for_static_preview' },
    { id: 'desktop_app', label: 'Desktop App', goal: 'Package Buddy for Mac, Windows, and Linux after the web dashboard stabilizes.', status: 'planned_packager' },
    { id: 'mobile_app', label: 'Mobile App', goal: 'Package Buddy for iOS and Android with store-ready packets.', status: 'planned_packager' },
  ],
  app_store_targets: [
    { id: 'apple_app_store', label: 'Apple App Store', approval_required: ['developer_account_use', 'submit_for_review'] },
    { id: 'google_play', label: 'Google Play', approval_required: ['developer_account_use', 'submit_for_review'] },
    { id: 'desktop_downloads', label: 'Desktop Downloads', approval_required: ['ship_installer', 'sign_release'] },
    { id: 'game_stores', label: 'Game Stores', approval_required: ['submit_store_listing', 'publish_public_release'] },
    { id: 'tv_stores', label: 'TV Stores', approval_required: ['submit_store_listing', 'publish_public_release'] },
  ],
  task_manager_layers: ['inbox_capture', 'goal_to_project', 'project_to_tasks', 'bot_assignment', 'approval_queue', 'evidence_tracker', 'deadline_and_reminder_queue', 'client_status_room', 'download_release_tracker', 'money_opportunity_pipeline'],
  web_research_policy: {
    allowed_sources: ['public web pages', 'official docs', 'public pricing pages', 'public marketplace listings', 'public reviews'],
    blocked_sources: ['private accounts without approval', 'paywalled or login-only data without permission', 'personal data brokers'],
    must_store: ['source_url', 'checked_at', 'summary', 'confidence', 'next_safe_action'],
  },
  approval_wall: ['buy_domain', 'sell_domain', 'change_dns', 'submit_app_store_listing', 'publish_public_release', 'send_customer_outreach', 'run_paid_ads', 'charge_or_move_money'],
};

const FALLBACK_BOT_CONTRACT_DISCOVERY = {
  generated_at: null,
  mission: 'Make every DreamCo bot continuously search for contract, grant, RFP, procurement, partnership, supplier, app-store, and service opportunities that match its division and business model.',
  default_mode: 'public_source_discovery_and_draft_only',
  search_cadence: {
    market_scan: 'daily',
    deep_match_review: 'weekly',
    client_opportunity_digest: 'weekly',
    stale_opportunity_cleanup: 'daily',
  },
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
  opportunity_types: ['government_contract', 'local_procurement', 'private_rfp', 'grant', 'vendor_registration', 'supplier_contract', 'trucking_route_contract', 'subcontracting_opportunity'],
  source_categories: [
    { id: 'public_procurement', label: 'Public Procurement', examples: ['federal opportunity portals', 'state procurement portals', 'city and county bids'], allowed_actions: ['search', 'summarize', 'score'] },
    { id: 'private_rfp_sources', label: 'Private RFP Sources', examples: ['company vendor pages', 'marketplace RFP listings'], allowed_actions: ['search', 'summarize', 'prepare outreach draft'] },
  ],
  approval_gates: ['submit_bid', 'submit_grant_application', 'register_vendor_account', 'contact_buyer', 'contact_supplier', 'sign_contract', 'accept_terms', 'spend_money'],
  top_opportunity_types: [
    { opportunity_type: 'client_service_opportunity', bot_count: 1248 },
    { opportunity_type: 'private_rfp', bot_count: 1248 },
    { opportunity_type: 'partnership_opportunity', bot_count: 1248 },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      opportunity_types: ['client_service_opportunity', 'private_rfp', 'partnership_opportunity'],
      sample_search_prompt: 'Search public and owner-approved sources for Buddy Bot contract opportunities.',
      dashboard_status: 'ready_for_contract_discovery',
    },
  ],
};

const FALLBACK_AI_DATA_PACKAGE_LIBRARY = {
  generated_at: null,
  mission: 'Create governed AI data packages that DreamCo can sell or license for model training, fine-tuning, retrieval, benchmarking, evaluation, and agent simulation.',
  positioning: 'DreamCo sells rights-cleared, quality-scored, metadata-rich AI data packages.',
  langchain: {
    required: true,
    javascript_packages: ['langchain', '@langchain/core', 'zod'],
    use_cases: ['document loading', 'chunking', 'metadata normalization', 'retrieval datasets', 'agent test sets'],
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
    { id: 'instruction_tuning', label: 'Instruction Tuning', buyer_use: 'Improve task following, customer support, and business workflow agents.', formats: ['jsonl', 'parquet'] },
    { id: 'rag_knowledge_base', label: 'RAG Knowledge Base', buyer_use: 'Power retrieval systems with chunked, cited, metadata-rich documents.', formats: ['jsonl', 'markdown'] },
    { id: 'eval_benchmark', label: 'Eval Benchmark', buyer_use: 'Test models, agents, tools, safety, and domain performance.', formats: ['jsonl', 'csv'] },
    { id: 'agent_simulation', label: 'Agent Simulation', buyer_use: 'Train and test agents on multi-step business workflows.', formats: ['jsonl', 'yaml'] },
  ],
  quality_gates: ['rights_clearance', 'pii_scan', 'deduplication', 'schema_validation', 'source_traceability', 'data_card_complete'],
  commercial_models: ['one_time_dataset_license', 'subscription_data_feed', 'custom_dataset_build', 'evaluation_benchmark_license'],
  approval_gates: ['sell_or_license_dataset', 'use_client_data', 'include_personal_data', 'publish_sample_records', 'share_buyer_preview'],
  top_package_types: [
    { package_type: 'instruction_tuning', bot_count: 1248 },
    { package_type: 'eval_benchmark', bot_count: 1248 },
    { package_type: 'agent_simulation', bot_count: 1248 },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      package_types: ['instruction_tuning', 'eval_benchmark', 'agent_simulation'],
      sample_package_name: 'Buddy Bot Training and Eval Data Pack',
      sample_buyer_use: 'Train, evaluate, or retrieve knowledge for CommandCore workflows.',
    },
  ],
};

const FALLBACK_PEOPLE_JOB_QUALIFICATION = {
  generated_at: null,
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
    allowed_sources: ['self-provided resume or profile', 'owner-approved CRM records', 'public professional profiles', 'public company pages'],
    blocked_sources: ['private accounts without approval', 'sensitive personal data', 'protected-class inference', 'background checks without compliant provider'],
  },
  qualification_lanes: [
    { id: 'candidate_resume_match', label: 'Candidate Resume Match', purpose: 'Compare self-provided resumes or application materials against a job description using role requirements and evidence notes.', outputs: ['skills_match', 'experience_evidence', 'gap_notes'] },
    { id: 'contractor_vendor_match', label: 'Contractor and Vendor Match', purpose: 'Research public contractor/vendor profiles, portfolios, capabilities, reviews, and fit for a project.', outputs: ['vendor_shortlist', 'capability_match', 'risk_notes'] },
    { id: 'sales_people_research', label: 'Sales People Research', purpose: 'Prepare compliant lead or stakeholder research from public and approved sources for owner-reviewed outreach.', outputs: ['stakeholder_map', 'public_profile_summary'] },
  ],
  approval_gates: ['collect_personal_data', 'store_person_profile', 'contact_person', 'send_outreach', 'make_hiring_decision', 'reject_candidate', 'run_background_check'],
  blocked_uses: ['automated_hiring_or_rejection', 'protected_class_scoring', 'background_screening_without_compliant_provider', 'mass_unsolicited_outreach'],
  top_qualification_lanes: [
    { qualification_lane: 'candidate_resume_match', bot_count: 1248 },
    { qualification_lane: 'employee_role_fit', bot_count: 1248 },
    { qualification_lane: 'sales_people_research', bot_count: 1248 },
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      qualification_lanes: ['candidate_resume_match', 'employee_role_fit', 'sales_people_research'],
      sample_lookup_prompt: 'Prepare a privacy-safe people or job-qualification lookup packet for Buddy Bot.',
    },
  ],
};

const FALLBACK_BOT_OWNER_SETTINGS = {
  generated_at: null,
  mission: 'Treat every DreamCo bot, including high-risk or previously blocked bots, as a supervised business-owner bot with clear on/off controls, permissions, approval gates, and safe-mode guardrails.',
  default_mode: 'business_owner_safe_mode',
  summary: {
    bot_count: 1248,
    bots_with_owner_settings: 1248,
    business_owner_enabled_bots: 1248,
    safe_mode_enabled_bots: 1248,
    high_risk_bots: 120,
    high_risk_bots_unblocked_for_safe_work: 120,
    live_action_approval_required_bots: 1248,
    settings_controls_ready: 12,
    permission_groups_ready: 5,
    guardrails_ready: 6,
    all_bots_have_on_off_controls: true,
  },
  global_settings: [
    { id: 'business_owner_mode', label: 'Business Owner Mode', default: true, description: 'Bot may research, plan, draft, test, package, and prepare business opportunities.' },
    { id: 'sandbox_mode', label: 'Sandbox Mode', default: true, description: 'Bot may run local tests, generated fixtures, simulations, and dry-run workflows.' },
    { id: 'contract_discovery', label: 'Contract Discovery', default: true, description: 'Bot may search public and owner-approved opportunities.' },
    { id: 'client_outreach', label: 'Client Outreach', default: false, description: 'Bot may only send outreach after explicit approval.' },
    { id: 'paid_actions', label: 'Paid Actions', default: false, description: 'Bot may only spend money or use paid APIs after approval.' },
    { id: 'money_movement', label: 'Money Movement', default: false, description: 'Bot may only move money after approval.' },
  ],
  permission_groups: [
    { id: 'safe_business_work', label: 'Safe Business Work', default: true, permissions: ['research', 'draft', 'score', 'simulate', 'sandbox_test'] },
    { id: 'external_impact', label: 'External Impact', default: false, permissions: ['send_outreach', 'submit_bid', 'publish_listing'] },
    { id: 'financial_impact', label: 'Financial Impact', default: false, permissions: ['charge_payment', 'issue_refund', 'buy_domain'] },
  ],
  always_require_approval: ['send_outreach', 'submit_bid', 'publish_app_or_store_listing', 'buy_domain', 'run_paid_ad', 'collect_or_move_money', 'production_deploy'],
  guardrails: [
    'Safe mode stays on by default for every bot.',
    'High-risk bots can work like other bots in sandbox and business-owner mode.',
    'Settings toggles expose capability state but do not bypass approval gates.',
  ],
  dashboard_sample: [
    {
      slug: 'buddy-bot',
      name: 'Buddy Bot',
      division: 'CommandCore',
      risk_hint: 'standard',
      business_owner_status: 'enabled_safe_mode',
      safe_work_unblocked: true,
      live_actions_require_approval: true,
      controls: {
        bot_enabled: true,
        safe_mode_enabled: true,
        business_owner_mode_enabled: true,
        client_outreach_enabled: false,
        paid_actions_enabled: false,
        money_movement_enabled: false,
      },
    },
  ],
};

const FALLBACK_STRIPE_REVENUE_RESCUE = {
  generated_at: null,
  summary: {
    revenue_rescue_ready: false,
    checkout_ready_offers: 0,
    offers_checked: 0,
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
    blocker_count: 0,
  },
  revenue_blockers: [
    'Run the Stripe revenue rescue report to find checkout, webhook, offer, and payout blockers.',
  ],
  priority_fixes: [
    'Create live Stripe offers, connect customer buttons to live payment links, and confirm webhook events are arriving.',
  ],
  offers: [],
  safety_note: 'Secrets stay in environment variables or secure host secrets, never in the repository.',
};

const FALLBACK_PRODUCTION_APPROVAL_PACKETS = {
  generated_at: null,
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
    money_movement: 0,
    financial_or_trading: 0,
    security_or_defense: 0,
  },
  packets: [],
  next_actions: [
    'Review approval-required bots by risk category before enabling live actions.',
    'Approve only the specific live actions each bot is allowed to perform.',
    'Keep risky external actions blocked until owner approval is recorded.',
  ],
};

const FALLBACK_BUDDY_OPS_QUEUE = {
  schema: 'dreamco.buddy_ops_queue.v1',
  count: 0,
  operations: [],
};

const FALLBACK_BUDDY_BOT_CONNECTIONS = {
  generated_at: null,
  summary: {
    all_bots_connected_to_buddy: true,
    all_bots_testable_from_actions_page: true,
    all_bots_have_custom_resources: true,
    all_bots_ready: true,
    bot_count: 0,
    buddy_connected_bots: 0,
    actions_page_testable_bots: 0,
    custom_resource_ready_bots: 0,
    failed_bots: 0,
    resources_per_bot_required: 100,
  },
  failures: [],
};

const BUILD_STAGES = [
  ['01', 'Specify', 'Identity, goal, inputs, outputs, limits, owner'],
  ['02', 'Compose', 'Tools, API, webhook, workflow, skills'],
  ['03', 'Sandbox', 'Fixtures, denied network, test secrets, timeouts'],
  ['04', 'Validate', 'Schema, unit, integration, security, evidence'],
  ['05', 'Review', 'Diff, risk summary, approval requests, rollback'],
  ['06', 'Publish', 'Pull request only; no direct production mutation'],
];

const GITHUB_SIGNALS = [
  { title: 'Reusable workflows', detail: 'Build common validation once and call it through workflow_call.' },
  { title: 'Least privilege', detail: 'Declare the smallest GITHUB_TOKEN permissions for every job.' },
  { title: 'Immutable dependencies', detail: 'Prefer reviewed full-length action commit references.' },
  { title: 'Webhook integrity', detail: 'Verify HMAC-SHA256, deduplicate delivery IDs, and filter events.' },
  { title: 'Fast webhook intake', detail: 'Acknowledge quickly, then process deliveries through a queue.' },
  { title: 'API restraint', detail: 'Use authenticated conditional reads and back off on rate limits.' },
];

const SAFETY_GATES = [
  'No live credentials in generated fixtures',
  'No payments, purchases, transfers, or ad spend',
  'No external outreach or publishing',
  'Network denied until explicitly allowed',
  'Resource and execution time limits',
  'Pull request and human review before deployment',
];

const BUDDY_LIVE_SYSTEMS = [
  { label: 'Client showcase', status: 'online', detail: 'Actions page is ready for guided demos and project walkthroughs.' },
  { label: 'Buddy console', status: 'supervised', detail: 'Commands queue locally with evidence, test, and approval policies visible.' },
  { label: 'Bot catalog', status: 'synced', detail: 'Inventory data powers search, capabilities, risk gates, and sandbox packets.' },
  { label: 'GitHub Pages', status: 'configured', detail: 'Static dashboard build includes the bot inventory for hosted previews.' },
];

const OPERATIONS_FEED = [
  ['05:23', 'Buddy connection guard verified 1,248 testable bots and 100 resources per bot.'],
  ['05:18', 'AI Creation Studio lanes expanded for games, simulations, image editing, audio, dashboards, and research.'],
  ['05:12', 'Actions page prompt created a supervised Buddy operation packet.'],
  ['05:04', 'Payment alert guard added email and GitHub issue notification paths.'],
];

const LIVE_ENVIRONMENT_CHECKS = [
  ['Branch', 'codex/bot-test-dashboard'],
  ['Mode', 'supervised'],
  ['Release gate', 'pull request'],
  ['Risk posture', 'sandbox first'],
];

const PROGRESS_WEEKEND_GOALS = [
  {
    title: 'Verify the repository',
    outcome: 'One correct GitHub repository, clean branch status, pull/push path confirmed, and Actions failures visible.',
    proof: ['git status', 'remote verified', 'workflow failures listed'],
  },
  {
    title: 'Complete the bot inventory',
    outcome: 'Every bot has purpose, inputs, outputs, revenue opportunity, API notes, status, and test path.',
    proof: ['bot catalog', 'division coverage', 'ready or needs-work state'],
  },
  {
    title: 'Finish Buddy as dashboard controller',
    outcome: 'Buddy shows divisions, launches test packets, tracks errors, documents bots, and routes rebuild/debug work.',
    proof: ['Actions page', 'Buddy console', 'bot test catalog'],
  },
  {
    title: 'Test Mac and GitHub workflow',
    outcome: 'Clone, pull, push, and verify a small change from the laptop without breaking the branch.',
    proof: ['local branch', 'pushed commit', 'GitHub confirmation'],
  },
  {
    title: 'Pick five sellable bots',
    outcome: 'Choose the 5 bots most likely to make money this month and define signup, usage, pricing, and demo path.',
    proof: ['top 5 list', 'client offer', 'demo script'],
  },
];

const PROGRESS_WEEKEND_DONE = [
  'One verified GitHub repository',
  'Complete bot inventory',
  'Buddy central dashboard',
  'Top five production candidates',
  'Biggest bugs and missing features list',
];

const CONSOLIDATION_PRIORITIES = [
  {
    title: 'Stabilize repository',
    status: 'critical',
    metric: '58 PRs / 31 failed runs',
    action: 'Freeze expansion, triage PRs, repair required CI, and separate experiments from release gates.',
  },
  {
    title: 'Prove every bot',
    status: 'source of truth',
    metric: '1,051 profiles / 45 divisions',
    action: 'Make the master registry authoritative for IDs, status, runtime, entry points, schemas, permissions, and ownership.',
  },
  {
    title: 'Fix public identity',
    status: 'in progress',
    metric: 'README corrected',
    action: 'Separate designed profiles from working bots, remove unsupported claims, and document local-first ownership.',
  },
  {
    title: 'Make Buddy real control',
    status: 'building',
    metric: 'approval/risk/spend gates',
    action: 'Connect Buddy routing to registry scoring, fallback selection, task plans, approvals, and cancellation.',
  },
  {
    title: 'Operational dashboard',
    status: 'building',
    metric: 'fleet/failure/PR/cost centers',
    action: 'Create one official dashboard for bot fleet, divisions, failures, PRs, costs, revenue, and customer workspaces.',
  },
  {
    title: 'Trustworthy autonomy',
    status: 'planned',
    metric: 'Guided / Semi / Full',
    action: 'Enforce autonomy modes, permissions, audit logs, memory export/delete, golden tasks, shadow tests, and rollback.',
  },
];

const CONSOLIDATION_FIRST_TEN = [
  'Correct registry and README counts',
  'Classify all profiles by implementation status',
  'Triage open pull requests',
  'Repair required CI pipeline',
  'Complete Command Center consolidation decision',
  'Make Buddy use the registry for real routing',
  'Enforce approval, risk, spending, and autonomy',
  'Launch Bot Fleet and Failure Center',
  'Make five bot products work end to end',
  'Publish DreamCo 1.0 readiness scorecard',
];

const TOP_100_UPDATE_GROUPS = [
  {
    priority: 'Repository stability',
    count: 20,
    focus: 'Branches, PR triage, failed workflows, required CI, report loops, runtime pins, and cost budgets.',
    firstMove: 'Make one required CI workflow and classify the 58 open PRs.',
  },
  {
    priority: 'Bot truth registry',
    count: 20,
    focus: 'Authoritative IDs, implementation status, runtime status, entry points, schemas, capabilities, ownership, and maturity.',
    firstMove: 'Generate public catalog only from the master registry.',
  },
  {
    priority: 'Public docs and identity',
    count: 15,
    focus: 'Counts, status pages, repository map, installation guide, data ownership, glossary, divisions, and capability matrix.',
    firstMove: 'Keep README claims tied to measurable evidence.',
  },
  {
    priority: 'Buddy control plane',
    count: 15,
    focus: 'Weighted routing, fallbacks, task decomposition, dependency-aware execution, approvals, risk, spending, and model budgets.',
    firstMove: 'Replace first-match routing with scored registry routing.',
  },
  {
    priority: 'Operational dashboard',
    count: 15,
    focus: 'Bot Fleet, Division Explorer, start/stop/test controls, timeline, failure center, PR center, cost, revenue, owner, and customer modes.',
    firstMove: 'Launch Bot Fleet plus Failure Center as the official dashboard surface.',
  },
  {
    priority: 'Trustworthy autonomy',
    count: 15,
    focus: 'Autonomy levels, operating modes, permissions, audit log, local-first memory, export/delete, golden tasks, shadow tests, and rollback.',
    firstMove: 'Enforce Guided, Semi-Automatic, and Full Automatic as code policies.',
  },
];

const ROYAL_PANEL_CLASS = 'border border-amber-500/40 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.16),transparent_34%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(6,78,59,0.5),rgba(15,23,42,0.98))] shadow-[0_24px_80px_rgba(0,0,0,0.45)]';
const ROYAL_CARD_CLASS = 'border border-amber-500/30 bg-slate-950/75 shadow-inner shadow-amber-950/30';
const ROYAL_TEXT_CLASS = 'bg-gradient-to-r from-amber-200 via-yellow-100 to-emerald-200 bg-clip-text text-transparent';

const DEBUGGING_OS_STAGES = [
  {
    stage: 'Capture',
    detail: 'Collect failing checks, logs, changed files, affected bots, screenshots, and user impact before guessing.',
    evidence: ['workflow run', 'error output', 'changed files'],
  },
  {
    stage: 'Reproduce',
    detail: 'Run the smallest local command that proves the failure and records the exact command used.',
    evidence: ['local command', 'exit code', 'test path'],
  },
  {
    stage: 'Isolate',
    detail: 'Separate source bug, config bug, dependency bug, data bug, integration bug, and flaky test risk.',
    evidence: ['root-cause category', 'blast radius', 'owner area'],
  },
  {
    stage: 'Patch',
    detail: 'Make the smallest reviewed change, keep unrelated files untouched, and preserve rollback notes.',
    evidence: ['diff summary', 'rollback plan', 'approval gate'],
  },
  {
    stage: 'Verify',
    detail: 'Run targeted tests first, then dashboard, storage, Stripe, bot, and cleanroom checks when affected.',
    evidence: ['test results', 'reports', 'remaining risk'],
  },
  {
    stage: 'Package',
    detail: 'Turn the fix into a client-ready explanation, PR checklist, demo note, and next action.',
    evidence: ['PR summary', 'client note', 'handoff status'],
  },
];

const SELLABLE_DEBUG_PACKAGES = [
  ['Launch Audit', 'Find broken checkout, bot tests, deploy blockers, repo health, and dashboard gaps before a client demo.'],
  ['AI App Debug Desk', 'Turn failing app, bot, workflow, API, webhook, and UI issues into tracked fix packets.'],
  ['Revenue Rescue', 'Trace Stripe links, offers, webhooks, payment alerts, and dashboard revenue evidence.'],
  ['Vibe Build QA', 'Review games, simulations, videos, courses, image edits, and dashboards for rights, tests, and handoff.'],
];

const PR_BUDDY_HELP_FLOW = [
  ['Scan', 'Buddy reads PR goal, changed files, comments, checks, linked issues, and stale risk.'],
  ['Explain', 'Buddy summarizes what changed, why it matters, what is risky, and what should be tested.'],
  ['Retest', 'Buddy queues targeted test commands and records pass/fail evidence before review.'],
  ['Repair', 'Buddy creates a supervised operation packet for any failing gate or missing evidence.'],
  ['Package', 'Buddy prepares a merge-ready checklist, rollback note, and client-safe summary.'],
];

const FAILED_PR_RESCUE_FLOW = [
  ['Find blocker', 'Read failing checks, review comments, merge conflicts, stale branch state, and linked issue goals.'],
  ['Build fix plan', 'Map each failed check to files, commands, likely cause, owner area, and smallest safe patch.'],
  ['Apply safely', 'Prepare a supervised patch packet, keep unrelated files untouched, and record rollback notes.'],
  ['Retest proof', 'Rerun targeted tests, dashboard checks, and workflow-equivalent commands before asking for review.'],
  ['Review packet', 'Write the PR comment summary with what failed, what changed, what passed, and what still needs owner approval.'],
];

const FAILED_PR_OWNER_GATES = [
  'Buddy can prepare fixes, test notes, PR comments, and retry instructions.',
  'Buddy does not merge, close, deploy, spend money, or change credentials without owner approval.',
  'Failed PRs stay in the rescue queue until failing checks are green or the remaining blocker is clearly assigned.',
];

const PAST_FAILURE_REBUILD_FLOW = [
  ['Import', 'Pull past failed PRs, workflow runs, quality gates, agent failures, and integration blockers into one backlog.'],
  ['Replay', 'Recreate the smallest safe sandbox scenario that proves the old failure still matters or is already fixed.'],
  ['Build', 'Create the missing patch, test, bot packet, workflow repair, or documentation needed to close the failure.'],
  ['Verify', 'Run the matching retest command and capture the dashboard, workflow, or report evidence.'],
  ['Close loop', 'Mark rebuilt, still blocked, duplicate, or owner approval needed with a client-safe note.'],
];

const PAST_FAILURE_REBUILD_GATES = [
  'Past failures are rebuilt from evidence, not guessed from titles alone.',
  'Resolved failures still get a regression test or proof note so they do not silently return.',
  'Each rebuild packet keeps source, age, target, fix type, retest proof, and owner approval state.',
];

const FAILURE_DEBUG_ROUTES = [
  ['Action workflow', 'Capture logs, job name, branch, commit, failed step, and rerun eligibility.'],
  ['Quality gate', 'Parse exact file, syntax error, command, affected package, and smallest repro test.'],
  ['Agent or bot', 'Check heartbeat, workflow status, test packet, resource library, and risk approval.'],
  ['Integration', 'Trace API, webhook, payment, storage, email, and notification evidence in sandbox first.'],
  ['Client demo', 'Package impact, screenshot, fix plan, verification command, and handoff note.'],
];

const FAILURE_DEBUG_GATES = [
  'Every failure gets an owner, source, command, suspected cause, next fix, and retest command.',
  'Buddy may prepare patches and pull request notes, but live deploys, merges, payments, and outreach wait for approval.',
  'A failure is not called fixed until the matching test, workflow, or dashboard evidence is recorded.',
  'Known flaky failures are tracked separately and still require a retry plan, timeout check, or quarantine note.',
];

const CLIENT_WORKFLOWS = [
  ['Discover', 'Show prospects what the bot fleet can build, test, and operate.'],
  ['Prototype', 'Prepare tools, APIs, webhooks, workflows, skills, and sandbox checks.'],
  ['Validate', 'Use test files, readiness states, and repository evidence before client handoff.'],
  ['Launch', 'Move approved work through pull requests, Pages previews, and deployment gates.'],
];

const COMPANY_BUILDER_PILLARS = [
  {
    title: 'AI companies',
    detail: 'Package bots as sellable business units with offer, website, workflows, dashboard, and client delivery plan.',
  },
  {
    title: 'AI departments',
    detail: 'Launch division-level teams with manager agents, specialist bots, task queues, KPIs, and shared memory.',
  },
  {
    title: 'AI employees',
    detail: 'Treat every bot as a supervised worker with job description, tools, permissions, tests, learning, and audit trail.',
  },
  {
    title: 'Human trust',
    detail: 'Buddy explains evidence, asks for approval, blocks risky live actions, and keeps ownership with the operator.',
  },
];

const VIBE_STUDIO_LANES = [
  {
    title: 'App or bot',
    icon: '🤖',
    prompt: 'Build a client-ready bot, app, dashboard, API, webhook, and sandbox test packet.',
    outputs: ['working prototype', 'bot prospectus', 'API/webhook plan', 'test loop'],
  },
  {
    title: 'Music video',
    icon: '🎬',
    prompt: 'Create an original music video plan with storyboard, shot list, visual prompts, timeline, and rights checks.',
    outputs: ['concept', 'storyboard', 'scene prompts', 'edit timeline'],
  },
  {
    title: 'Kids learning video',
    icon: '🧒',
    prompt: 'Create age-safe lessons with story, narration, visuals, quiz, captions, and parent or teacher notes.',
    outputs: ['lesson script', 'visual plan', 'quiz', 'safety notes'],
  },
  {
    title: 'College course',
    icon: '🎓',
    prompt: 'Build a course with modules, lessons, assignments, rubrics, labs, slides, and outcomes.',
    outputs: ['syllabus', 'modules', 'assessments', 'instructor pack'],
  },
  {
    title: 'Video game',
    icon: '🎮',
    prompt: 'Design and prototype rules, levels, characters, scoring, save state, tests, and deployment path.',
    outputs: ['game design doc', 'playable prototype', 'level plan', 'QA checklist'],
  },
  {
    title: 'Simulation',
    icon: '🧪',
    prompt: 'Build business, science, training, finance, real estate, operations, or emergency simulation scenarios.',
    outputs: ['scenario model', 'controls', 'metrics', 'sandbox runbook'],
  },
  {
    title: 'Photo and image editor',
    icon: '🖼️',
    prompt: 'Plan image edits, product mockups, restoration, background changes, brand graphics, and asset variants with rights checks.',
    outputs: ['edit brief', 'asset list', 'variant prompts', 'rights log'],
  },
  {
    title: 'Design and brand studio',
    icon: '🎨',
    prompt: 'Create logos, landing page direction, ad creatives, social graphics, slide themes, and brand kits.',
    outputs: ['brand kit', 'creative brief', 'layout plan', 'export checklist'],
  },
  {
    title: 'Documents and presentations',
    icon: '📄',
    prompt: 'Build proposals, pitch decks, contracts, SOPs, worksheets, reports, and client handoff documents.',
    outputs: ['document outline', 'deck plan', 'review checklist', 'handoff pack'],
  },
  {
    title: 'Data dashboard',
    icon: '📊',
    prompt: 'Turn spreadsheets, metrics, Stripe data, bot reports, and client KPIs into dashboards and decision views.',
    outputs: ['data model', 'charts', 'filters', 'quality checks'],
  },
  {
    title: 'Automation workflow',
    icon: '⚙️',
    prompt: 'Design repeatable automations for emails, CRMs, webhooks, scheduling, support, inventory, and operations.',
    outputs: ['workflow map', 'API plan', 'webhook plan', 'failure handling'],
  },
  {
    title: '3D or AR experience',
    icon: '🧊',
    prompt: 'Plan product viewers, walkthroughs, learning labs, interactive spaces, and lightweight 3D simulations.',
    outputs: ['scene spec', 'asset list', 'interaction map', 'performance checks'],
  },
  {
    title: 'Audio and voice project',
    icon: '🎙️',
    prompt: 'Create podcast packets, voiceover scripts, sound design plans, narration flows, and consent-safe voice workflows.',
    outputs: ['script', 'audio plan', 'consent log', 'publish checklist'],
  },
  {
    title: 'Research and writing',
    icon: '🔎',
    prompt: 'Research markets, competitors, grants, customers, products, legal basics, scientific topics, and source-backed reports.',
    outputs: ['source map', 'summary', 'citations', 'action plan'],
  },
];

const VIBE_STUDIO_GATES = [
  'Written consent before cloning a real person voice, face, likeness, or image',
  'AI-generated and AI-edited media labels stay visible in the asset record',
  'No political, legal, medical, financial, emergency, or public-safety impersonation',
  'No cloning minors or creating sexual/degrading fake media of real people',
  'No fake testimonials, founders, employees, endorsements, or authority figures',
  'Every asset stores consent proof, source, creator, timestamp, and usage rights',
];

const VIBE_BUILD_FLOW = [
  ['Prompt', 'Client describes the outcome, audience, style, budget, and safety limits.'],
  ['Packet', 'Buddy creates the script, design doc, asset plan, build steps, and test checklist.'],
  ['Prototype', 'Buddy builds the first app, course, game, video plan, or simulation in sandbox mode.'],
  ['Review', 'Client approves rights, safety, factual claims, age fit, brand fit, and deployment path.'],
  ['Ship', 'Buddy exports files, opens a pull request, or prepares a client demo page.'],
];

const COMPETITIVE_BUILD_ROADMAP = [
  {
    capability: 'One-prompt app and bot flow',
    status: 'building',
    proof: 'Turn a client prompt into plan, files, tests, dashboard, and pull request packet.',
  },
  {
    capability: 'Live preview while building',
    status: 'planned',
    proof: 'Stream generated UI, routes, logs, screenshots, and test status into the dashboard.',
  },
  {
    capability: 'One-click deploy',
    status: 'planned',
    proof: 'Package approved builds for GitHub Pages, static hosting, and production deployment gates.',
  },
  {
    capability: 'Built-in auth, database, storage, payments, email, and webhooks',
    status: 'building',
    proof: 'Use per-bot API, webhook, sandbox, storage, and approval policies before live credentials.',
  },
  {
    capability: 'Rollback and checkpoints',
    status: 'building',
    proof: 'Create build packets with diff summary, rollback plan, branch, commit, and test evidence.',
  },
  {
    capability: 'Visual editing',
    status: 'planned',
    proof: 'Let clients revise layout, copy, assets, scenes, lessons, and game screens from preview feedback.',
  },
  {
    capability: 'Voice input',
    status: 'planned',
    proof: 'Capture spoken build requests while keeping consent, identity, and media rights checks active.',
  },
  {
    capability: 'Image-to-app and screenshot-to-dashboard',
    status: 'planned',
    proof: 'Convert uploaded screenshots or sketches into UI structure, components, tests, and demo pages.',
  },
  {
    capability: 'Eval/test loop after every generated change',
    status: 'building',
    proof: 'Run schema, syntax, sandbox, storage, readiness, and dashboard checks before client handoff.',
  },
];

const BEST_COMPETITIVE_PATH = [
  {
    phase: '01',
    title: 'Win the trust lane first',
    timeframe: 'now',
    focus: 'Make Buddy the safest way to build apps, bots, media packets, courses, games, and simulations.',
    proof: ['approval gates', 'rights checks', 'storage guard', 'test evidence'],
  },
  {
    phase: '02',
    title: 'Ship one-prompt build packets',
    timeframe: 'next',
    focus: 'Turn one client prompt into a plan, files, sandbox preview, tests, rollback notes, and prospectus page.',
    proof: ['build packet', 'dashboard preview', 'pull request', 'client handoff'],
  },
  {
    phase: '03',
    title: 'Own bot businesses, not just apps',
    timeframe: 'near term',
    focus: 'Package every build as an AI employee, department, or company with tools, APIs, webhooks, memory, and dashboards.',
    proof: ['bot profile', 'service library', 'workflow library', 'money approval rules'],
  },
  {
    phase: '04',
    title: 'Add live preview and visual revision',
    timeframe: 'build track',
    focus: 'Let clients watch Buddy build, then revise layouts, scenes, lessons, screenshots, and game screens from preview feedback.',
    proof: ['preview route', 'screenshot evidence', 'visual edit queue', 'responsive checks'],
  },
  {
    phase: '05',
    title: 'Bundle essential business services',
    timeframe: 'build track',
    focus: 'Offer safe starter paths for auth, database, storage, payments, email, webhooks, and deployment.',
    proof: ['sandbox credentials', 'service templates', 'integration tests', 'one-click deploy gate'],
  },
  {
    phase: '06',
    title: 'Make quality automatic',
    timeframe: 'always',
    focus: 'Run evaluations after every generated change and block risky releases until evidence is clean.',
    proof: ['syntax checks', 'sandbox tests', 'storage checks', 'readiness reports'],
  },
];

function formatLabel(value) {
  return String(value || '').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function percent(value, total) {
  if (!total) return 0;
  return Math.max(0, Math.min(100, Math.round((Number(value || 0) / Number(total)) * 100)));
}

function formatDateTime(value) {
  if (!value) return 'generated fallback';
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

async function fetchFirstJson(paths) {
  let lastError;
  for (const path of paths) {
    try {
      const response = await fetch(path);
      if (!response.ok) throw new Error(`${path} returned ${response.status}`);
      return await response.json();
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

function getCapabilityLabels(bot, limit = 6) {
  return (bot?.capabilities ?? [])
    .map((capability) => {
      if (typeof capability === 'string') return capability;
      return capability.label ?? formatLabel(capability.intent);
    })
    .filter(Boolean)
    .slice(0, limit);
}

function buildBotCatalog(inventory) {
  const source = inventory?.bots?.length
    ? inventory.bots
    : [
        ...(inventory?.buddy_bots ?? []),
        ...(inventory?.attention?.production_blockers ?? []),
        ...FALLBACK_BUDDY_INVENTORY.buddy_bots,
      ];
  const bySlug = new Map();
  source.forEach((bot) => {
    if (bot?.slug) bySlug.set(bot.slug, bot);
  });
  return [...bySlug.values()].sort((a, b) => {
    const aBuddy = String(a.slug).includes('buddy') ? 0 : 1;
    const bBuddy = String(b.slug).includes('buddy') ? 0 : 1;
    return aBuddy - bBuddy || String(a.name).localeCompare(String(b.name));
  });
}

function buildBotTestPacket(bot, scope = 'selected') {
  const capabilities = getCapabilityLabels(bot, 8);
  return {
    scope,
    slug: bot.slug,
    name: bot.name,
    command: 'python3 tools/run_generated_bot_smoke.py',
    mode: 'sandbox_only',
    tests: bot.tests ?? [],
    approval: bot.risk_hint === 'high' || bot.production_readiness_status === 'production_candidate_approval_required'
      ? 'buddy_money_help_approval_required_before_live_actions'
      : 'safe_for_sandbox_testing',
    canDo: {
      forYou: bot.description || `${bot.name} helps operate ${bot.division || 'its division'} workflows.`,
      forUsers: capabilities.length
        ? `Users can get ${capabilities.slice(0, 3).join(', ')}.`
        : 'Users can get governed bot assistance once its capabilities are expanded.',
      forBuddy: `Buddy can route this bot through sandbox tests, inspect ${formatNumber(bot.test_count)} test file(s), and keep its ${formatLabel(bot.test_state)} state visible.`,
    },
  };
}

function buildFailureDebugQueue({ triage, stewardship, storage, stripeRescue, buddyConnections }) {
  const qualityFailures = (stewardship.quality_checks ?? [])
    .flatMap((check) => (check.failures ?? []).map((failure) => ({
      id: `quality-${check.name}-${failure.file}`,
      source: 'Quality gate',
      title: `${formatLabel(check.name)} failure`,
      target: failure.file,
      evidence: failure.error,
      route: 'smallest local syntax or test command',
      action: 'Patch the file, rerun the gate, and package the diff with rollback notes.',
    })));

  const workflowFailures = (triage.failed_workflow_runs ?? []).map((run) => ({
    id: `workflow-${run.id}`,
    source: 'Action workflow',
    title: run.name,
    target: run.branch,
    evidence: `${formatLabel(run.conclusion)} · ${formatDateTime(run.updated_at)}`,
    route: 'workflow log capture and targeted rerun',
    action: 'Inspect failed job logs, reproduce locally when possible, then queue a supervised repair packet.',
  }));

  const botFailures = (buddyConnections.failures ?? []).map((failure, index) => ({
    id: `bot-${failure.bot_id ?? failure.slug ?? index}`,
    source: 'Agent or bot',
    title: failure.name ?? failure.bot_id ?? 'Bot connection failure',
    target: failure.division ?? failure.slug ?? 'bot registry',
    evidence: failure.reason ?? failure.message ?? 'Connection, resource, or testability failure detected.',
    route: 'bot test packet and resource guard',
    action: 'Reconnect Buddy route, verify custom resources, and rerun the bot connection guard.',
  }));

  const storageFailures = [
    ...(storage.checks ?? []).filter((check) => check.status === 'fail').map((check) => ({
      id: `storage-${check.name}`,
      source: 'Storage guard',
      title: formatLabel(check.name),
      target: 'local-first storage policy',
      evidence: (check.failures ?? []).slice(0, 2).join(' · ') || check.message,
      route: 'manifest, shard, budget, and compaction check',
      action: 'Shard large files, preserve summary manifests, rerun the storage guard, and record evidence.',
    })),
    ...(storage.warnings ?? []).map((warning, index) => ({
      id: `storage-warning-${index}`,
      source: 'Storage warning',
      title: 'Memory storage warning',
      target: 'future memory safety',
      evidence: warning,
      route: 'budget warning review',
      action: 'Convert warning into a tracked storage ticket before it becomes a blocking failure.',
    })),
  ];

  const revenueFailures = (stripeRescue.revenue_blockers ?? []).map((blocker, index) => ({
    id: `revenue-${index}`,
    source: 'Revenue integration',
    title: 'Payment flow blocker',
    target: 'Stripe, email, or GitHub payment notice',
    evidence: blocker,
    route: 'sandbox payment trace',
    action: 'Trace offer, checkout link, webhook event, email recipient, and GitHub notification path.',
  }));

  return [
    ...qualityFailures,
    ...workflowFailures,
    ...botFailures,
    ...storageFailures,
    ...revenueFailures,
  ].slice(0, 12);
}

function buildPastFailureRebuildPackets({ triage, stewardship, stripeRescue, buddyConnections }) {
  const prPackets = (triage.pr_restart_queue ?? []).map((pr) => ({
    id: `past-pr-${pr.number}`,
    source: 'Past PR failure',
    title: `#${pr.number} ${pr.title}`,
    target: pr.head_branch,
    build: 'Rebase or retest, inspect comments, repair gates, and write review-ready notes.',
    proof: (pr.restart_reasons ?? []).map(formatLabel).join(', ') || 'Restart reason pending',
  }));

  const workflowPackets = (triage.failed_workflow_runs ?? []).map((run) => ({
    id: `past-workflow-${run.id}`,
    source: 'Past workflow failure',
    title: run.name,
    target: run.branch,
    build: 'Recreate failed job locally when possible, patch the cause, then capture retest proof.',
    proof: `${formatLabel(run.conclusion)} · ${formatDateTime(run.updated_at)}`,
  }));

  const qualityPackets = (stewardship.quality_checks ?? [])
    .filter((check) => check.status !== 'pass' || (check.failures ?? []).length > 0)
    .map((check) => ({
      id: `past-quality-${check.name}`,
      source: 'Past quality failure',
      title: formatLabel(check.name),
      target: `${formatNumber(check.scanned)} file(s) scanned`,
      build: 'Patch syntax or schema issue, add focused test coverage, and rerun the quality gate.',
      proof: `${formatNumber((check.failures ?? []).length)} failure(s)`,
    }));

  const botPackets = (buddyConnections.failures ?? []).map((failure, index) => ({
    id: `past-bot-${failure.bot_id ?? failure.slug ?? index}`,
    source: 'Past agent failure',
    title: failure.name ?? failure.bot_id ?? 'Bot connection failure',
    target: failure.division ?? failure.slug ?? 'bot registry',
    build: 'Rebuild Buddy route, resources, sandbox test packet, and connection proof.',
    proof: failure.reason ?? failure.message ?? 'Bot connection guard failure',
  }));

  const revenuePackets = (stripeRescue.revenue_blockers ?? []).map((blocker, index) => ({
    id: `past-revenue-${index}`,
    source: 'Past revenue blocker',
    title: 'Payment path rebuild',
    target: 'Stripe, email, and GitHub payment notice path',
    build: 'Rebuild offer, checkout link, webhook event proof, and payment notification evidence.',
    proof: blocker,
  }));

  return [
    ...prPackets,
    ...workflowPackets,
    ...qualityPackets,
    ...botPackets,
    ...revenuePackets,
  ].slice(0, 16);
}

export default function ActionsPage({
  ActionsMonitorComponent = ActionsMonitor,
  onBuddyCommandSubmit = () => {},
  onBuildRequest = () => {},
  onBotTestRequest = () => {},
}) {
  const [showBuddyCenter, setShowBuddyCenter] = useState(false);
  const [selectedBuilderId, setSelectedBuilderId] = useState('full-bot-system');
  const [activeLibrary, setActiveLibrary] = useState('tools');
  const [botSearch, setBotSearch] = useState('');
  const [selectedBotSlug, setSelectedBotSlug] = useState('buddy-bot');
  const [botTestPacket, setBotTestPacket] = useState(null);
  const [libraryData, setLibraryData] = useState(null);
  const [libraryStatus, setLibraryStatus] = useState('loading');
  const [buddyInventory, setBuddyInventory] = useState(null);
  const [buddyInventoryStatus, setBuddyInventoryStatus] = useState('loading');
  const [githubTriage, setGithubTriage] = useState(null);
  const [githubTriageStatus, setGithubTriageStatus] = useState('loading');
  const [repositoryStewardship, setRepositoryStewardship] = useState(null);
  const [repositoryStewardshipStatus, setRepositoryStewardshipStatus] = useState('loading');
  const [buddyProductivity, setBuddyProductivity] = useState(null);
  const [buddyProductivityStatus, setBuddyProductivityStatus] = useState('loading');
  const [releaseReadiness, setReleaseReadiness] = useState(null);
  const [releaseReadinessStatus, setReleaseReadinessStatus] = useState('loading');
  const [appFoundry, setAppFoundry] = useState(null);
  const [appFoundryStatus, setAppFoundryStatus] = useState('loading');
  const [botFounderAppStore, setBotFounderAppStore] = useState(null);
  const [botFounderAppStoreStatus, setBotFounderAppStoreStatus] = useState('loading');
  const [dailyScaling, setDailyScaling] = useState(null);
  const [dailyScalingStatus, setDailyScalingStatus] = useState('loading');
  const [buddyCodexCheapOps, setBuddyCodexCheapOps] = useState(null);
  const [buddyCodexCheapOpsStatus, setBuddyCodexCheapOpsStatus] = useState('loading');
  const [specializedKnowledge, setSpecializedKnowledge] = useState(null);
  const [specializedKnowledgeStatus, setSpecializedKnowledgeStatus] = useState('loading');
  const [aiAgentModelLibrary, setAiAgentModelLibrary] = useState(null);
  const [aiAgentModelLibraryStatus, setAiAgentModelLibraryStatus] = useState('loading');
  const [businessLaunchExpansion, setBusinessLaunchExpansion] = useState(null);
  const [businessLaunchExpansionStatus, setBusinessLaunchExpansionStatus] = useState('loading');
  const [buddyCommercePublishing, setBuddyCommercePublishing] = useState(null);
  const [buddyCommercePublishingStatus, setBuddyCommercePublishingStatus] = useState('loading');
  const [botContractDiscovery, setBotContractDiscovery] = useState(null);
  const [botContractDiscoveryStatus, setBotContractDiscoveryStatus] = useState('loading');
  const [aiDataPackageLibrary, setAiDataPackageLibrary] = useState(null);
  const [aiDataPackageLibraryStatus, setAiDataPackageLibraryStatus] = useState('loading');
  const [peopleJobQualification, setPeopleJobQualification] = useState(null);
  const [peopleJobQualificationStatus, setPeopleJobQualificationStatus] = useState('loading');
  const [botOwnerSettings, setBotOwnerSettings] = useState(null);
  const [botOwnerSettingsStatus, setBotOwnerSettingsStatus] = useState('loading');
  const [storageGuard, setStorageGuard] = useState(null);
  const [storageGuardStatus, setStorageGuardStatus] = useState('loading');
  const [stripeRevenueRescue, setStripeRevenueRescue] = useState(null);
  const [stripeRevenueRescueStatus, setStripeRevenueRescueStatus] = useState('loading');
  const [productionApprovalPackets, setProductionApprovalPackets] = useState(null);
  const [productionApprovalPacketsStatus, setProductionApprovalPacketsStatus] = useState('loading');
  const [buildPacket, setBuildPacket] = useState(null);
  const [buddyOpsQueue, setBuddyOpsQueue] = useState(null);
  const [buddyOpsStatus, setBuddyOpsStatus] = useState('loading');
  const [aggressiveModeStatus, setAggressiveModeStatus] = useState('ready');
  const [buddyBotConnections, setBuddyBotConnections] = useState(null);
  const [buddyBotConnectionsStatus, setBuddyBotConnectionsStatus] = useState('loading');

  useEffect(() => {
    fetchFirstJson(['/api/system-libraries'])
      .then((data) => {
        setLibraryData(data);
        setLibraryStatus('live');
      })
      .catch(() => setLibraryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/buddy-capabilities', './data/buddy_capability_inventory.json'])
      .then((data) => {
        setBuddyInventory(data);
        setBuddyInventoryStatus(data?.branch ? 'static inventory' : 'live');
      })
      .catch(() => setBuddyInventoryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/github-triage'])
      .then((data) => {
        setGithubTriage(data);
        setGithubTriageStatus('live');
      })
      .catch(() => setGithubTriageStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/repository-stewardship'])
      .then((data) => {
        setRepositoryStewardship(data);
        setRepositoryStewardshipStatus('live');
      })
      .catch(() => setRepositoryStewardshipStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/buddy-productivity'])
      .then((data) => {
        setBuddyProductivity(data);
        setBuddyProductivityStatus('live');
      })
      .catch(() => setBuddyProductivityStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/release-readiness'])
      .then((data) => {
        setReleaseReadiness(data);
        setReleaseReadinessStatus('live');
      })
      .catch(() => setReleaseReadinessStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/app-foundry'])
      .then((data) => {
        setAppFoundry(data);
        setAppFoundryStatus('live');
      })
      .catch(() => setAppFoundryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/bot-founder-app-store'])
      .then((data) => {
        setBotFounderAppStore(data);
        setBotFounderAppStoreStatus('live');
      })
      .catch(() => setBotFounderAppStoreStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/24-hour-scaling'])
      .then((data) => {
        setDailyScaling(data);
        setDailyScalingStatus('live');
      })
      .catch(() => setDailyScalingStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/buddy-codex-cheap-ops'])
      .then((data) => {
        setBuddyCodexCheapOps(data);
        setBuddyCodexCheapOpsStatus('live');
      })
      .catch(() => setBuddyCodexCheapOpsStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/specialized-bot-knowledge'])
      .then((data) => {
        setSpecializedKnowledge(data);
        setSpecializedKnowledgeStatus('live');
      })
      .catch(() => setSpecializedKnowledgeStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/ai-agent-model-library'])
      .then((data) => {
        setAiAgentModelLibrary(data);
        setAiAgentModelLibraryStatus('live');
      })
      .catch(() => setAiAgentModelLibraryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/business-launch-expansion'])
      .then((data) => {
        setBusinessLaunchExpansion(data);
        setBusinessLaunchExpansionStatus('live');
      })
      .catch(() => setBusinessLaunchExpansionStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/buddy-commerce-publishing'])
      .then((data) => {
        setBuddyCommercePublishing(data);
        setBuddyCommercePublishingStatus('live');
      })
      .catch(() => setBuddyCommercePublishingStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/bot-contract-discovery'])
      .then((data) => {
        setBotContractDiscovery(data);
        setBotContractDiscoveryStatus('live');
      })
      .catch(() => setBotContractDiscoveryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/ai-data-package-library'])
      .then((data) => {
        setAiDataPackageLibrary(data);
        setAiDataPackageLibraryStatus('live');
      })
      .catch(() => setAiDataPackageLibraryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/people-job-qualification'])
      .then((data) => {
        setPeopleJobQualification(data);
        setPeopleJobQualificationStatus('live');
      })
      .catch(() => setPeopleJobQualificationStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/bot-owner-settings'])
      .then((data) => {
        setBotOwnerSettings(data);
        setBotOwnerSettingsStatus('live');
      })
      .catch(() => setBotOwnerSettingsStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/storage-guard'])
      .then((data) => {
        setStorageGuard(data);
        setStorageGuardStatus('live');
      })
      .catch(() => setStorageGuardStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/stripe-revenue-rescue'])
      .then((data) => {
        setStripeRevenueRescue(data);
        setStripeRevenueRescueStatus('live');
      })
      .catch(() => setStripeRevenueRescueStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/production-approval-packets'])
      .then((data) => {
        setProductionApprovalPackets(data);
        setProductionApprovalPacketsStatus('live');
      })
      .catch(() => setProductionApprovalPacketsStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/buddy-ops'])
      .then((data) => {
        setBuddyOpsQueue(data);
        setBuddyOpsStatus('live');
      })
      .catch(() => setBuddyOpsStatus('local only'));
  }, []);

  useEffect(() => {
    fetchFirstJson(['/api/buddy-bot-connections'])
      .then((data) => {
        setBuddyBotConnections(data);
        setBuddyBotConnectionsStatus('live');
      })
      .catch(() => setBuddyBotConnectionsStatus('generated fallback'));
  }, []);

  const builders = libraryData?.builders ?? FALLBACK_BUILDERS;
  const libraries = libraryData?.libraries ?? FALLBACK_LIBRARIES;
  const bootcampBaseline = libraryData?.bootcamp_baseline ?? FALLBACK_BOOTCAMP_BASELINE;
  const libraryCoverage = libraryData?.coverage ?? {};
  const botCount = libraryData?.bot_count ?? 1247;
  const inventory = buddyInventory ?? FALLBACK_BUDDY_INVENTORY;
  const triage = githubTriage ?? FALLBACK_GITHUB_TRIAGE;
  const stewardship = repositoryStewardship ?? FALLBACK_REPOSITORY_STEWARDSHIP;
  const productivity = buddyProductivity ?? FALLBACK_BUDDY_PRODUCTIVITY;
  const readiness = releaseReadiness ?? FALLBACK_RELEASE_READINESS;
  const foundry = appFoundry ?? FALLBACK_APP_FOUNDRY;
  const botFounderStore = botFounderAppStore ?? FALLBACK_BOT_FOUNDER_APP_STORE;
  const scaling24 = dailyScaling ?? FALLBACK_24_HOUR_SCALING;
  const codexCheapOps = buddyCodexCheapOps ?? FALLBACK_BUDDY_CODEX_CHEAP_OPS;
  const knowledge = specializedKnowledge ?? FALLBACK_SPECIALIZED_BOT_KNOWLEDGE;
  const modelLibrary = aiAgentModelLibrary ?? FALLBACK_AI_AGENT_MODEL_LIBRARY;
  const businessLaunch = businessLaunchExpansion ?? FALLBACK_BUSINESS_LAUNCH_EXPANSION;
  const commercePublishing = buddyCommercePublishing ?? FALLBACK_BUDDY_COMMERCE_PUBLISHING;
  const contractDiscovery = botContractDiscovery ?? FALLBACK_BOT_CONTRACT_DISCOVERY;
  const dataPackageLibrary = aiDataPackageLibrary ?? FALLBACK_AI_DATA_PACKAGE_LIBRARY;
  const peopleLookup = peopleJobQualification ?? FALLBACK_PEOPLE_JOB_QUALIFICATION;
  const ownerSettings = botOwnerSettings ?? FALLBACK_BOT_OWNER_SETTINGS;
  const storage = storageGuard ?? FALLBACK_STORAGE_GUARD;
  const stripeRescue = stripeRevenueRescue ?? FALLBACK_STRIPE_REVENUE_RESCUE;
  const approvalPackets = productionApprovalPackets ?? FALLBACK_PRODUCTION_APPROVAL_PACKETS;
  const buddyOps = buddyOpsQueue ?? FALLBACK_BUDDY_OPS_QUEUE;
  const buddyConnections = buddyBotConnections ?? FALLBACK_BUDDY_BOT_CONNECTIONS;
  const inventorySummary = inventory.summary ?? FALLBACK_BUDDY_INVENTORY.summary;
  const triageSummary = triage.summary ?? FALLBACK_GITHUB_TRIAGE.summary;
  const stewardshipSummary = stewardship.summary ?? FALLBACK_REPOSITORY_STEWARDSHIP.summary;
  const productivitySummary = productivity.summary ?? FALLBACK_BUDDY_PRODUCTIVITY.summary;
  const readinessSummary = readiness.summary ?? FALLBACK_RELEASE_READINESS.summary;
  const foundrySummary = foundry.summary ?? FALLBACK_APP_FOUNDRY.summary;
  const botFounderSummary = botFounderStore.summary ?? FALLBACK_BOT_FOUNDER_APP_STORE.summary;
  const scaling24Summary = scaling24.summary ?? FALLBACK_24_HOUR_SCALING.summary;
  const codexCheapOpsSummary = codexCheapOps.summary ?? FALLBACK_BUDDY_CODEX_CHEAP_OPS.summary;
  const knowledgeSummary = knowledge.summary ?? FALLBACK_SPECIALIZED_BOT_KNOWLEDGE.summary;
  const modelLibrarySummary = modelLibrary.summary ?? FALLBACK_AI_AGENT_MODEL_LIBRARY.summary;
  const businessLaunchSummary = businessLaunch.summary ?? FALLBACK_BUSINESS_LAUNCH_EXPANSION.summary;
  const commercePublishingSummary = commercePublishing.summary ?? FALLBACK_BUDDY_COMMERCE_PUBLISHING.summary;
  const contractDiscoverySummary = contractDiscovery.summary ?? FALLBACK_BOT_CONTRACT_DISCOVERY.summary;
  const dataPackageSummary = dataPackageLibrary.summary ?? FALLBACK_AI_DATA_PACKAGE_LIBRARY.summary;
  const peopleLookupSummary = peopleLookup.summary ?? FALLBACK_PEOPLE_JOB_QUALIFICATION.summary;
  const ownerSettingsSummary = ownerSettings.summary ?? FALLBACK_BOT_OWNER_SETTINGS.summary;
  const storageSummary = storage.summary ?? FALLBACK_STORAGE_GUARD.summary;
  const stripeRescueSummary = stripeRescue.summary ?? FALLBACK_STRIPE_REVENUE_RESCUE.summary;
  const approvalPacketSummary = approvalPackets.summary ?? FALLBACK_PRODUCTION_APPROVAL_PACKETS.summary;
  const buddyConnectionSummary = buddyConnections.summary ?? FALLBACK_BUDDY_BOT_CONNECTIONS.summary;
  const buildStates = inventorySummary.build_states ?? {};
  const testStates = inventorySummary.test_states ?? {};
  const codingPathStates = inventorySummary.coding_path_states ?? {};
  const productionStates = inventorySummary.production_readiness_states ?? {};
  const needsImplementation = inventory.attention?.needs_implementation ?? [];
  const needsDirectTests = inventory.attention?.needs_direct_test_coverage ?? [];
  const needsSystemMapping = inventory.attention?.needs_existing_system_mapping ?? [];
  const directBuddyBots = inventory.buddy_bots ?? [];
  const botCatalog = useMemo(() => buildBotCatalog(inventory), [inventory]);
  const selectedBot = botCatalog.find((bot) => bot.slug === selectedBotSlug) ?? botCatalog[0] ?? FALLBACK_BUDDY_INVENTORY.buddy_bots[0];
  const selectedBotCapabilities = getCapabilityLabels(selectedBot, 8);
  const visibleBots = useMemo(() => {
    const query = botSearch.trim().toLowerCase();
    return botCatalog
      .filter((bot) => {
        if (!query) return true;
        const haystack = [
          bot.slug,
          bot.name,
          bot.division,
          bot.category,
          bot.description,
          ...getCapabilityLabels(bot, 12),
        ].join(' ').toLowerCase();
        return haystack.includes(query);
      })
      .slice(0, 12);
  }, [botCatalog, botSearch]);
  const selectedBuilder = builders.find((builder) => builder.id === selectedBuilderId) ?? builders[0];
  const selectedLibrary = libraries.find((library) => library.id === activeLibrary) ?? libraries[0];
  const contractCount = useMemo(
    () => libraries.reduce((total, library) => total + Number(library.count || 0), 0),
    [libraries],
  );
  const failureDebugQueue = useMemo(
    () => buildFailureDebugQueue({
      triage,
      stewardship,
      storage,
      stripeRescue,
      buddyConnections,
    }),
    [triage, stewardship, storage, stripeRescue, buddyConnections],
  );
  const pastFailureRebuildPackets = useMemo(
    () => buildPastFailureRebuildPackets({
      triage,
      stewardship,
      stripeRescue,
      buddyConnections,
    }),
    [triage, stewardship, stripeRescue, buddyConnections],
  );

  function prepareBuildPacket() {
    const packet = {
      builder: selectedBuilder.name,
      outputs: selectedBuilder.outputs,
      mode: 'sandbox_and_pull_request',
      approval: selectedBuilder.approval,
    };
    setBuildPacket(packet);
    onBuildRequest(packet);
  }

  async function submitBuddyPrompt(prompt) {
    const response = await fetch('/api/buddy-ops/prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        requested_by: 'actions_page',
        target: selectedBot?.slug ?? 'dreamcobots',
      }),
    });
    if (!response.ok) {
      throw new Error(`Buddy operation API returned ${response.status}`);
    }
    const data = await response.json();
    const packet = data.packet;
    setBuildPacket({
      builder: packet.builder,
      outputs: packet.outputs,
      mode: packet.mode,
      approval: 'pull_request_review_required',
      id: packet.id,
      operation_type: packet.operation_type,
    });
    setBuddyOpsQueue((current) => {
      const existing = current ?? FALLBACK_BUDDY_OPS_QUEUE;
      return {
        ...existing,
        count: Number(existing.count || 0) + 1,
        operations: [packet, ...(existing.operations ?? [])].slice(0, 25),
      };
    });
    setBuddyOpsStatus('live');
    onBuddyCommandSubmit(packet);
    return { packet };
  }

  async function activateAggressiveMode() {
    setAggressiveModeStatus('activating');
    const response = await fetch('/api/buddy-ops/aggressive-mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        requested_by: 'actions_page',
        target: 'dreamcobots',
      }),
    });
    if (!response.ok) {
      setAggressiveModeStatus('error');
      throw new Error(`Aggressive Mode API returned ${response.status}`);
    }
    const activation = await response.json();
    const packets = activation.packets ?? [];
    setBuildPacket({
      builder: 'Aggressive Mode 24-Hour Repository Sweep',
      outputs: ['repository-wide packet queue', 'local checks', 'cost guardrails', 'approval gates'],
      mode: activation.mode,
      approval: 'owner_approval_for_live_or_paid_actions',
      id: activation.id,
      operation_type: 'aggressive_mode_activation',
    });
    setBuddyOpsQueue((current) => {
      const existing = current ?? FALLBACK_BUDDY_OPS_QUEUE;
      return {
        ...existing,
        count: Number(existing.count || 0) + packets.length,
        operations: [...packets].reverse().concat(existing.operations ?? []).slice(0, 25),
      };
    });
    setBuddyOpsStatus('aggressive queued');
    setAggressiveModeStatus('queued');
    onBuddyCommandSubmit(activation);
    return activation;
  }

  function prepareBotTest(bot, scope = 'selected') {
    const packet = buildBotTestPacket(bot, scope);
    setSelectedBotSlug(bot.slug);
    setBotTestPacket(packet);
    onBotTestRequest(packet);
  }

  return (
    <section className="space-y-6">
      <header className={`relative overflow-hidden ${ROYAL_PANEL_CLASS}`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/80 to-transparent" />
        <div className="pointer-events-none absolute right-8 top-6 h-24 w-24 rounded-full border border-amber-300/20 bg-amber-300/10 blur-2xl" />
        <div className="grid gap-6 p-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">Royal Client Operations Preview</p>
              <span className="rounded-full border border-emerald-400/40 bg-emerald-950/50 px-3 py-1 text-xs font-semibold text-emerald-200">
                Live dashboard
              </span>
              <span className="rounded-full border border-amber-400/50 bg-amber-950/30 px-3 py-1 text-xs font-semibold text-amber-200">
                Supervised autonomy
              </span>
            </div>
            <h2 className={`mt-3 max-w-4xl text-3xl font-black tracking-normal md:text-4xl ${ROYAL_TEXT_CLASS}`}>
              Buddy Command Tower for building, testing, and presenting bot systems
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
              A client-ready view of what is built, what Buddy can operate, which bots are testable,
              and which workflows are ready for safe review, demo, and deployment.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setShowBuddyCenter(true)}
                className="rounded-md border border-amber-300/60 bg-gradient-to-r from-amber-500 to-yellow-600 px-4 py-2 text-sm font-semibold text-slate-950 shadow-lg shadow-amber-950/30 hover:from-amber-400 hover:to-yellow-500"
              >
                Open Buddy Live Console
              </button>
              <button
                type="button"
                onClick={() => prepareBotTest(botCatalog.find((bot) => bot.slug === 'buddy-bot') ?? selectedBot, 'buddy')}
                className="rounded-md border border-emerald-300/40 bg-emerald-950/30 px-4 py-2 text-sm font-semibold text-emerald-100 hover:border-emerald-200"
              >
                Prepare Buddy Test
              </button>
              <button
                type="button"
                onClick={activateAggressiveMode}
                disabled={aggressiveModeStatus === 'activating'}
                className="rounded-md border border-rose-300/50 bg-rose-950/40 px-4 py-2 text-sm font-semibold text-rose-100 hover:border-rose-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {aggressiveModeStatus === 'activating' ? 'Queuing Aggressive Mode' : 'Aggressive Mode 24h'}
              </button>
            </div>
          </div>
          <aside className={`${ROYAL_CARD_CLASS} p-4`}>
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold text-white">Operational status</h3>
              <span className="rounded-full border border-emerald-400/40 bg-emerald-950/40 px-2 py-0.5 text-[11px] font-semibold uppercase text-emerald-200">
                Live
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-px overflow-hidden border border-amber-500/20 bg-amber-500/20">
              {LIVE_ENVIRONMENT_CHECKS.map(([label, value]) => (
                <div key={label} className="bg-slate-950/90 p-3">
                  <p className="truncate text-xs font-semibold text-white">{value}</p>
                  <p className="mt-1 text-[11px] uppercase tracking-wide text-amber-200/70">{label}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 space-y-3">
              {BUDDY_LIVE_SYSTEMS.map((system) => (
                <div key={system.label} className="border-l-2 border-dreamco-accent pl-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-white">{system.label}</p>
                    <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                      {system.status}
                    </span>
                  </div>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{system.detail}</p>
                </div>
              ))}
            </div>
          </aside>
        </div>

        <div className="grid grid-cols-2 gap-px border-t border-amber-500/20 bg-amber-500/20 lg:grid-cols-4">
          {[
            ['Registered bots', botCount.toLocaleString()],
            ['Per-bot contracts', contractCount.toLocaleString()],
            ['System builders', builders.length],
            ['Generated libraries', libraries.length],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-950/90 p-4">
              <p className="text-2xl font-black text-amber-100">{value}</p>
              <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{label}</p>
            </div>
          ))}
        </div>
      </header>

      <section aria-labelledby="live-feed-heading" className="grid gap-5 xl:grid-cols-[1fr_24rem]">
        <div className="border border-slate-700 bg-slate-950 p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase text-dreamco-accent">Live evidence stream</p>
              <h3 id="live-feed-heading" className="mt-1 text-lg font-semibold text-white">Recent Buddy operations</h3>
            </div>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
              Updated from repo reports
            </span>
          </div>
          <div className="mt-4 divide-y divide-slate-800 border border-slate-800 bg-slate-900">
            {OPERATIONS_FEED.map(([time, detail]) => (
              <div key={`${time}-${detail}`} className="grid grid-cols-[4rem_1fr] gap-3 p-3">
                <span className="font-mono text-xs text-dreamco-accent">{time}</span>
                <p className="text-sm leading-5 text-slate-300">{detail}</p>
              </div>
            ))}
          </div>
        </div>

        <aside className="border border-slate-700 bg-slate-950 p-5">
          <p className="text-xs font-bold uppercase text-dreamco-accent">Fleet readiness</p>
          <h3 className="mt-1 text-lg font-semibold text-white">Operational proof</h3>
          <div className="mt-4 space-y-4">
            {[
              ['Buddy connected', buddyConnectionSummary.buddy_connected_bots, buddyConnectionSummary.bot_count],
              ['Actions testable', buddyConnectionSummary.actions_page_testable_bots, buddyConnectionSummary.bot_count],
              ['Custom resources', buddyConnectionSummary.custom_resource_ready_bots, buddyConnectionSummary.bot_count],
              ['Production ready', inventorySummary.production_ready_bots, inventorySummary.bot_profiles_scanned],
            ].map(([label, value, total]) => {
              const width = percent(value, total);
              return (
                <div key={label}>
                  <div className="flex items-center justify-between gap-3 text-xs">
                    <span className="font-semibold text-slate-200">{label}</span>
                    <span className="font-mono text-slate-500">{width}%</span>
                  </div>
                  <div className="mt-2 h-2 overflow-hidden bg-slate-800">
                    <div className="h-full bg-dreamco-accent" style={{ width: `${width}%` }} />
                  </div>
                  <p className="mt-1 text-[11px] text-slate-500">{formatNumber(value)} / {formatNumber(total)}</p>
                </div>
              );
            })}
          </div>
        </aside>
      </section>

      <section aria-labelledby="progress-weekend-heading" className={`relative overflow-hidden p-5 ${ROYAL_PANEL_CLASS}`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/70 to-transparent" />
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">DreamCo progress weekend</p>
            <h3 id="progress-weekend-heading" className={`mt-1 text-lg font-semibold ${ROYAL_TEXT_CLASS}`}>
              Make the current system reliable, organized, and demonstrable
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              This keeps Buddy focused on proving the repository, bot inventory, dashboard control, Mac/GitHub workflow,
              sellable bot shortlist, and bug list before expanding into more new systems.
            </p>
          </div>
          <span className="rounded-full border border-amber-400/40 bg-amber-950/30 px-3 py-1 text-xs font-semibold text-amber-200">
            Sunday night milestone
          </span>
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-amber-500/20 bg-amber-500/20 lg:grid-cols-5">
          {PROGRESS_WEEKEND_GOALS.map((goal, index) => (
            <article key={goal.title} className="min-h-52 bg-slate-950/90 p-4">
              <p className="font-mono text-xs text-amber-200">0{index + 1}</p>
              <h4 className="mt-2 text-sm font-semibold text-white">{goal.title}</h4>
              <p className="mt-2 text-xs leading-5 text-slate-400">{goal.outcome}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {goal.proof.map((item) => (
                  <span key={item} className="rounded-full border border-amber-500/20 px-2 py-1 text-[11px] text-amber-100">
                    {item}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>

        <div className="mt-5 border border-amber-500/20 bg-slate-950/70 p-4">
          <h4 className="text-sm font-semibold text-amber-100">Done means</h4>
          <div className="mt-3 grid gap-2 md:grid-cols-5">
            {PROGRESS_WEEKEND_DONE.map((item) => (
              <div key={item} className="border-l-2 border-emerald-300/60 pl-3 text-xs leading-5 text-slate-300">
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="consolidation-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">DreamCo 1.0 consolidation</p>
            <h3 id="consolidation-heading" className="mt-1 text-lg font-semibold text-white">
              Convert the repository into one reliable operating platform
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              The next phase is proof and consolidation: stabilize CI, make the registry authoritative, route Buddy through real
              controls, finish one dashboard, and ship five end-to-end products before adding more divisions.
            </p>
          </div>
          <span className="rounded-full border border-yellow-800 bg-yellow-950/30 px-3 py-1 text-xs font-semibold text-yellow-300">
            expansion freeze until core proof
          </span>
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-3">
          {CONSOLIDATION_PRIORITIES.map((priority) => (
            <article key={priority.title} className="min-h-44 bg-slate-900 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="text-sm font-semibold text-white">{priority.title}</h4>
                  <p className="mt-1 font-mono text-[11px] text-dreamco-accent">{priority.metric}</p>
                </div>
                <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                  {priority.status}
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-slate-400">{priority.action}</p>
            </article>
          ))}
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <h4 className="text-sm font-semibold text-white">First ten execution updates</h4>
          <div className="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-5">
            {CONSOLIDATION_FIRST_TEN.map((item, index) => (
              <div key={item} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                <span className="font-mono text-dreamco-accent">{String(index + 1).padStart(2, '0')}</span> {item}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-white">Top 100 update backlog</h4>
              <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-400">
                Buddy should group the 100 updates into six proof categories, then build them in order instead of scattering effort across new ideas.
              </p>
            </div>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-300">
              {TOP_100_UPDATE_GROUPS.reduce((total, group) => total + group.count, 0)} updates mapped
            </span>
          </div>

          <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-3">
            {TOP_100_UPDATE_GROUPS.map((group) => (
              <article key={group.priority} className="min-h-44 bg-slate-950 p-4">
                <div className="flex items-start justify-between gap-3">
                  <h5 className="text-sm font-semibold text-white">{group.priority}</h5>
                  <span className="rounded-full border border-dreamco-accent/40 px-2 py-0.5 text-[11px] font-semibold text-dreamco-accent">
                    {group.count}
                  </span>
                </div>
                <p className="mt-3 text-xs leading-5 text-slate-400">{group.focus}</p>
                <p className="mt-3 border-l-2 border-yellow-500 pl-3 text-xs leading-5 text-yellow-100">{group.firstMove}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="mt-5 border border-emerald-700/40 bg-emerald-950/20 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-white">Done versus still-building comparison</h4>
              <p className="mt-1 max-w-3xl text-xs leading-5 text-emerald-100/80">
                Buddy compares the DreamCo 1.0 plan against actual repository evidence so the dashboard shows proof,
                active work, and unproven blockers without overclaiming production readiness.
              </p>
            </div>
            <span className="rounded-full border border-emerald-500/40 px-3 py-1 text-xs font-semibold text-emerald-200">
              {releaseReadinessStatus} · {formatDateTime(readiness.generated_at)}
            </span>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-px overflow-hidden border border-emerald-900 bg-emerald-900 lg:grid-cols-4 xl:grid-cols-8">
            {[
              ['Readiness', readinessSummary.release_readiness_score],
              ['First ten done', readinessSummary.first_ten_complete],
              ['First ten active', readinessSummary.first_ten_active],
              ['Unproven', readinessSummary.first_ten_blocked],
              ['Top groups active', readinessSummary.top_100_groups_active],
              ['Open PRs', readinessSummary.open_prs],
              ['Failed runs', readinessSummary.failed_workflow_runs],
              ['Ready bots', readinessSummary.production_ready_bots],
            ].map(([label, value]) => (
              <div key={label} className="bg-slate-950 p-4">
                <p className="text-xl font-black text-white">{typeof value === 'number' ? formatNumber(value) : String(value)}</p>
                <p className="mt-1 text-xs uppercase text-emerald-200/70">{label}</p>
              </div>
            ))}
          </div>

          <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
            <div className="border border-slate-800 bg-slate-950 p-4">
              <h5 className="text-sm font-semibold text-white">First ten execution proof</h5>
              <div className="mt-3 space-y-2">
                {(readiness.first_ten_updates ?? []).slice(0, 10).map((item, index) => (
                  <div key={item.id} className="grid gap-3 border border-slate-800 bg-slate-900 p-3 md:grid-cols-[2rem_minmax(0,1fr)_7rem]">
                    <span className="font-mono text-xs text-dreamco-accent">{String(index + 1).padStart(2, '0')}</span>
                    <div>
                      <p className="text-sm font-semibold text-white">{item.title}</p>
                      <p className="mt-1 text-xs leading-5 text-slate-400">{item.next}</p>
                    </div>
                    <span className={`h-fit rounded-full border px-2 py-1 text-center text-[11px] font-semibold uppercase ${
                      item.status === 'complete'
                        ? 'border-emerald-500/50 text-emerald-200'
                        : item.status === 'blocked'
                          ? 'border-rose-500/50 text-rose-200'
                          : 'border-amber-500/50 text-amber-200'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-5">
              <div className="border border-slate-800 bg-slate-950 p-4">
                <h5 className="text-sm font-semibold text-white">Top 100 group state</h5>
                <div className="mt-3 space-y-3">
                  {(readiness.top_100_groups ?? []).map((group) => (
                    <div key={group.id} className="border-b border-slate-800 pb-3 last:border-0 last:pb-0">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-xs font-semibold text-white">{formatLabel(group.title)}</p>
                        <span className="font-mono text-[11px] text-dreamco-accent">
                          {group.planned_updates} · {group.status}
                        </span>
                      </div>
                      <p className="mt-1 text-xs leading-5 text-slate-400">{group.next}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border border-slate-800 bg-slate-950 p-4">
                <h5 className="text-sm font-semibold text-white">Buddy next moves</h5>
                <div className="mt-3 space-y-2">
                  {(readiness.next_actions ?? []).slice(0, 4).map((action) => (
                    <p key={action} className="border-l-2 border-emerald-400 pl-3 text-xs leading-5 text-slate-300">
                      {action}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section aria-labelledby="client-flow-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Client presentation flow</p>
            <h3 id="client-flow-heading" className="mt-1 text-lg font-semibold text-white">Professional delivery pipeline</h3>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            GitHub Pages ready
          </span>
        </div>
        <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-4">
          {CLIENT_WORKFLOWS.map(([title, detail], index) => (
            <div key={title} className="min-h-32 bg-slate-900 p-4">
              <p className="font-mono text-xs text-dreamco-accent">0{index + 1}</p>
              <h4 className="mt-2 text-sm font-semibold text-white">{title}</h4>
              <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section aria-labelledby="buddy-ops-heading" className={`relative overflow-hidden p-5 ${ROYAL_PANEL_CLASS}`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/70 to-transparent" />
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">Royal Buddy operator console</p>
            <h3 id="buddy-ops-heading" className={`mt-1 text-lg font-semibold ${ROYAL_TEXT_CLASS}`}>
              Prompt Buddy from the Actions page
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Create governed operation packets for builds, tests, Stripe fixes, Vibe Studio work, deployments, and bot systems.
              Packets stay sandbox-first until approval gates are cleared.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowBuddyCenter(true)}
            className="rounded-md border border-amber-300/60 bg-gradient-to-r from-amber-500 to-yellow-600 px-4 py-2 text-sm font-semibold text-slate-950 shadow-lg shadow-amber-950/30 hover:from-amber-400 hover:to-yellow-500"
          >
            Open Buddy Operator
          </button>
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
          <aside className={`${ROYAL_CARD_CLASS} p-4`}>
            <h4 className="text-sm font-semibold text-white">Operation status</h4>
            <div className="mt-3 grid grid-cols-2 gap-px overflow-hidden border border-amber-500/20 bg-amber-500/20">
              {[
                ['Queue source', buddyOpsStatus],
                ['Packets', buddyOps.count],
                ['Mode', 'Sandbox first'],
                ['Approval', 'PR required'],
              ].map(([label, value]) => (
                <div key={label} className="bg-slate-950/90 p-3">
                  <p className="text-sm font-bold text-amber-100">{value}</p>
                  <p className="mt-1 text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 space-y-2">
              {[
                'External outreach blocked until approval',
                'Money movement blocked until approval',
                'Production deploy blocked until approval',
                'Credential changes blocked until approval',
              ].map((gate) => (
                <div key={gate} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                  {gate}
                </div>
              ))}
            </div>
          </aside>

          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Recent operation packets</h4>
            <div className="mt-3 space-y-3">
              {(buddyOps.operations ?? []).slice(0, 5).map((operation) => (
                <div key={operation.id} className="border border-slate-800 bg-slate-950 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-white">{operation.builder}</p>
                    <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                      {formatLabel(operation.operation_type)}
                    </span>
                  </div>
                  <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-400">{operation.prompt}</p>
                  <p className="mt-2 font-mono text-[11px] text-slate-500">{operation.id}</p>
                </div>
              ))}
              {(buddyOps.operations ?? []).length === 0 && (
                <p className="text-sm text-slate-400">No operation packets yet. Open Buddy Operator and type a prompt.</p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section aria-labelledby="vibe-studio-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Buddy Vibe Studio</p>
            <h3 id="vibe-studio-heading" className="mt-1 text-lg font-semibold text-white">
              AI Creation Studio for apps, games, simulations, media, and business systems
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Clients can describe what they want in plain language. Buddy turns it into a production packet, sandbox prototype,
              safety review, rights log, tests, and client-ready handoff.
            </p>
          </div>
          <span className="rounded-full border border-green-800 bg-green-950/30 px-3 py-1 text-xs font-semibold text-green-300">
            sandbox first · rights review required
          </span>
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {VIBE_STUDIO_LANES.map((lane) => (
            <article key={lane.title} className="min-h-56 bg-slate-900 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-2xl">{lane.icon}</p>
                  <h4 className="mt-2 text-sm font-semibold text-white">{lane.title}</h4>
                </div>
                <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-400">
                  vibe build
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-slate-400">{lane.prompt}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {lane.outputs.map((output) => (
                  <span key={output} className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300">
                    {output}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">One-prompt build flow</h4>
            <div className="mt-3 space-y-3">
              {VIBE_BUILD_FLOW.map(([title, detail], index) => (
                <div key={title} className="grid grid-cols-[2rem_1fr] gap-3">
                  <span className="font-mono text-xs text-dreamco-accent">0{index + 1}</span>
                  <div>
                    <p className="text-sm font-semibold text-white">{title}</p>
                    <p className="mt-1 text-xs leading-5 text-slate-400">{detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Voice and image consent rules</h4>
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              {VIBE_STUDIO_GATES.map((gate) => (
                <div key={gate} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                  {gate}
                </div>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="app-foundry-heading" className={`relative overflow-hidden p-5 ${ROYAL_PANEL_CLASS}`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/70 to-transparent" />
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">DreamCo App Foundry</p>
            <h3 id="app-foundry-heading" className={`mt-1 text-lg font-semibold ${ROYAL_TEXT_CLASS}`}>
              In-house A-to-Z builder, host, and deploy system
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              {foundry.mission}
            </p>
          </div>
          <span className="rounded-full border border-amber-400/50 bg-amber-950/30 px-3 py-1 text-xs font-semibold text-amber-200">
            {appFoundryStatus} · {formatDateTime(foundry.generated_at)}
          </span>
        </div>

        <div className="mt-5 border border-amber-500/20 bg-slate-950/70 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-amber-100">Own-code-first rule</h4>
              <p className="mt-2 max-w-4xl text-xs leading-5 text-slate-300">{foundry.ownership_rule}</p>
            </div>
            <span className="rounded-full border border-emerald-400/40 bg-emerald-950/30 px-3 py-1 text-xs font-semibold text-emerald-200">
              {formatLabel(foundry.operating_posture)}
            </span>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-amber-500/20 bg-amber-500/20 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Score', foundrySummary.readiness_score],
            ['Lanes', foundrySummary.creation_lanes],
            ['Systems', foundrySummary.in_house_systems],
            ['Deploy targets', foundrySummary.deployment_targets],
            ['Static ready', foundrySummary.static_or_configured_targets],
            ['Custom APIs', foundrySummary.custom_api_contracts],
            ['API bootcamps', foundrySummary.api_sandbox_bootcamps],
            ['Workflow gens', foundrySummary.sandbox_workflow_generators],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-950/90 p-4">
              <p className="text-xl font-black text-amber-100">{typeof value === 'number' ? formatNumber(value) : value}</p>
              <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-4">
          {(foundry.lanes ?? []).map((lane) => (
            <article key={lane.id} className="min-h-64 bg-slate-950 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase text-dreamco-accent">{formatLabel(lane.status)}</p>
                  <h4 className="mt-1 text-sm font-semibold text-white">{lane.label}</h4>
                </div>
                <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                  {lane.output_count ?? lane.outputs?.length ?? 0} outputs
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-slate-400">{lane.description}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(lane.outputs ?? []).slice(0, 4).map((output) => (
                  <span key={output} className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300">
                    {formatLabel(output)}
                  </span>
                ))}
              </div>
              <p className="mt-4 border-l-2 border-amber-300/70 pl-3 text-xs leading-5 text-amber-100/80">
                Hosts: {(lane.host_targets ?? []).map(formatLabel).join(', ')}
              </p>
            </article>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-950 p-4">
            <h4 className="text-sm font-semibold text-white">Deployment targets</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(foundry.deployment_targets ?? []).map((target) => (
                <div key={target.id} className="border border-slate-800 bg-slate-900 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-white">{target.label}</p>
                    <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                      {formatLabel(target.status)}
                    </span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{target.role}</p>
                </div>
              ))}
            </div>
          </div>
          <aside className="border border-slate-800 bg-slate-950 p-4">
            <h4 className="text-sm font-semibold text-white">Live deploy gates</h4>
            <div className="mt-3 space-y-2">
              {(foundry.quality_gates ?? []).slice(0, 8).map((gate) => (
                <div key={gate} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                  {formatLabel(gate)}
                </div>
              ))}
            </div>
            <div className="mt-4 border border-amber-900/70 bg-amber-950/20 p-3">
              <p className="text-xs font-semibold uppercase text-amber-200">Next build target</p>
              <p className="mt-2 text-xs leading-5 text-amber-100/80">{foundry.next_build_targets?.[0]}</p>
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="bot-founder-store-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Bot Founder App Store</p>
            <h3 id="bot-founder-store-heading" className="mt-1 text-lg font-semibold text-white">
              Every bot studies the market and prepares its own autonomous app business
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              {botFounderStore.mission}
            </p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {botFounderAppStoreStatus} · {formatDateTime(botFounderStore.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Founder packets', botFounderSummary.founder_packets],
            ['App concepts', botFounderSummary.bots_with_app_concept],
            ['Competitor plans', botFounderSummary.bots_with_competitor_study_plan],
            ['Revenue models', botFounderSummary.bots_with_revenue_model],
            ['Marketing plans', botFounderSummary.bots_with_marketing_plan],
            ['Customer discovery', botFounderSummary.bots_with_customer_discovery_plan],
            ['Store listings', botFounderSummary.bots_with_app_store_listing],
            ['Approval gated', botFounderSummary.bots_blocked_from_live_actions_until_approval],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 border border-amber-800 bg-amber-950/20 p-4">
          <h4 className="text-sm font-semibold text-amber-100">Live-action approval wall</h4>
          <p className="mt-2 text-xs leading-5 text-amber-100/80">{botFounderStore.live_action_policy}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {(botFounderStore.approval_gates ?? []).slice(0, 12).map((gate) => (
              <span key={gate} className="rounded-full border border-amber-500/30 px-3 py-1 text-xs text-amber-100">
                {formatLabel(gate)}
              </span>
            ))}
          </div>
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Founder study labs</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(botFounderStore.founder_study_loops ?? []).slice(0, 6).map((loop) => (
                <article key={loop.id} className="border border-slate-800 bg-slate-950 p-3">
                  <h5 className="text-sm font-semibold text-white">{loop.label}</h5>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{loop.purpose}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(loop.outputs ?? []).slice(0, 4).map((output) => (
                      <span key={output} className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300">
                        {formatLabel(output)}
                      </span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">App-store categories</h4>
            <div className="mt-3 space-y-2">
              {(botFounderStore.app_store_categories ?? []).slice(0, 10).map((item) => (
                <div key={item.category} className="flex items-center justify-between gap-3 border-b border-slate-800 pb-2">
                  <span className="text-xs uppercase text-slate-400">{formatLabel(item.category)}</span>
                  <span className="font-mono text-xs text-dreamco-accent">{formatNumber(item.bot_count)}</span>
                </div>
              ))}
            </div>
          </aside>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h4 className="text-sm font-semibold text-white">Sample bot-owned app-store packets</h4>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
              {formatNumber(botFounderSummary.bot_count)} bots preparing listings
            </span>
          </div>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {(botFounderStore.dashboard_sample ?? []).slice(0, 8).map((packet) => (
              <article key={packet.slug} className="border border-slate-800 bg-slate-950 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-lg">{packet.emoji}</p>
                    <h5 className="mt-1 text-sm font-semibold text-white">{packet.name}</h5>
                  </div>
                  <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                    {formatLabel(packet.app_store_category)}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-slate-400">{packet.autonomous_app_concept?.promise}</p>
                <p className="mt-3 border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                  Customer: {packet.target_customer}
                </p>
                <p className="mt-3 text-[11px] uppercase text-slate-500">
                  {formatLabel(packet.app_store_listing?.status)}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="scaling-24-heading" className={`relative overflow-hidden p-5 ${ROYAL_PANEL_CLASS}`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/70 to-transparent" />
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">24-hour scaling system</p>
            <h3 id="scaling-24-heading" className={`mt-1 text-lg font-semibold ${ROYAL_TEXT_CLASS}`}>
              Around-the-clock research, build, test, package, growth, and review cycles
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">{scaling24.mission}</p>
          </div>
          <span className="rounded-full border border-amber-400/50 bg-amber-950/30 px-3 py-1 text-xs font-semibold text-amber-200">
            {dailyScalingStatus} · {formatDateTime(scaling24.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-amber-500/20 bg-amber-500/20 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Readiness', scaling24Summary.readiness_score],
            ['Cycles', scaling24Summary.cycles_defined],
            ['Safe steps', scaling24Summary.safe_automation_steps],
            ['Approval steps', scaling24Summary.cycle_approval_steps],
            ['Blocked gates', scaling24Summary.always_blocked_gates],
            ['Scale lanes', scaling24Summary.scale_lanes],
            ['Min replicas', scaling24Summary.min_replicas],
            ['Max replicas', scaling24Summary.max_replicas],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-950/90 p-4">
              <p className="text-xl font-black text-amber-100">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 border border-emerald-500/30 bg-emerald-950/20 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-emerald-100">Buddy cheap Codex mode</h4>
              <p className="mt-2 max-w-3xl text-xs leading-5 text-emerald-100/80">
                {codexCheapOps.always_on_strategy?.plain_english}
              </p>
            </div>
            <span className="rounded-full border border-emerald-400/40 px-3 py-1 text-xs font-semibold text-emerald-100">
              {buddyCodexCheapOpsStatus} · {formatDateTime(codexCheapOps.generated_at)}
            </span>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-px overflow-hidden border border-emerald-500/20 bg-emerald-500/20 md:grid-cols-4 xl:grid-cols-8">
            {[
              ['Capabilities', codexCheapOpsSummary.codex_style_capabilities],
              ['Buddy bots', codexCheapOpsSummary.bots_connected_to_buddy],
              ['Low-cost AI', codexCheapOpsSummary.low_cost_ai_resources],
              ['Gemini', codexCheapOpsSummary.gemini_resources],
              ['GitHub guards', codexCheapOpsSummary.github_cost_guardrails],
              ['AI guards', codexCheapOpsSummary.ai_cost_guardrails],
              ['Aggressive runs', codexCheapOpsSummary.aggressive_mode_runs],
              ['Hard limits', codexCheapOpsSummary.aggressive_mode_hard_limits],
              ['Billing safe', codexCheapOpsSummary.billing_bypass_claimed ? 0 : 1],
              ['Honest autonomy', codexCheapOpsSummary.unlimited_autonomy_claimed ? 0 : 1],
            ].map(([label, value]) => (
              <div key={label} className="bg-slate-950/90 p-3">
                <p className="text-lg font-black text-emerald-100">{formatNumber(value)}</p>
                <p className="mt-1 text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {(codexCheapOps.codex_style_capabilities ?? []).slice(0, 6).map((capability) => (
              <article key={capability.id} className="border border-slate-800 bg-slate-950 p-3">
                <h5 className="text-sm font-semibold text-white">{capability.label}</h5>
                <p className="mt-2 text-xs leading-5 text-slate-400">{capability.buddy_can}</p>
                <p className="mt-2 border-l-2 border-emerald-400 pl-3 text-xs leading-5 text-emerald-100/80">
                  {capability.cheap_path}
                </p>
              </article>
            ))}
          </div>
          <div className="mt-4 border border-rose-500/30 bg-rose-950/20 p-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h5 className="text-sm font-semibold text-rose-100">Aggressive Mode 24-hour sweep</h5>
                <p className="mt-1 text-xs leading-5 text-rose-100/80">
                  Queues every safe repository, bot, report, test, failure-rebuild, cost-saver, and model-routing lane.
                </p>
              </div>
              <button
                type="button"
                onClick={activateAggressiveMode}
                disabled={aggressiveModeStatus === 'activating'}
                className="rounded-md border border-rose-300/50 bg-rose-900/50 px-3 py-2 text-xs font-semibold text-rose-50 hover:border-rose-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {aggressiveModeStatus === 'activating' ? 'Queuing' : 'Run Aggressive Mode'}
              </button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {(codexCheapOps.aggressive_mode_contract?.hard_limits ?? []).slice(0, 7).map((limit) => (
                <span key={limit} className="rounded-full border border-rose-400/30 px-2 py-1 text-[11px] text-rose-100">
                  {formatLabel(limit)}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-3">
          {(scaling24.daily_cycles ?? []).map((cycle) => (
            <article key={cycle.id} className="min-h-52 bg-slate-950 p-4">
              <div className="flex items-center justify-between gap-3">
                <h4 className="text-sm font-semibold text-white">{formatLabel(cycle.id)}</h4>
                <span className="font-mono text-xs text-dreamco-accent">{cycle.window}</span>
              </div>
              <p className="mt-3 text-xs leading-5 text-slate-400">{cycle.purpose}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(cycle.safe_automation ?? []).slice(0, 3).map((item) => (
                  <span key={item} className="rounded-full border border-emerald-500/30 px-2 py-1 text-[11px] text-emerald-100">
                    {formatLabel(item)}
                  </span>
                ))}
              </div>
              <p className="mt-4 border-l-2 border-amber-300/70 pl-3 text-xs leading-5 text-amber-100/80">
                Approval: {(cycle.approval_required ?? []).slice(0, 3).map(formatLabel).join(', ')}
              </p>
            </article>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-950 p-4">
            <h4 className="text-sm font-semibold text-white">Scale lanes</h4>
            <div className="mt-3 flex flex-wrap gap-2">
              {(scaling24.scale_lanes ?? []).map((lane) => (
                <span key={lane} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
                  {formatLabel(lane)}
                </span>
              ))}
            </div>
          </div>
          <aside className="border border-amber-900/70 bg-amber-950/20 p-4">
            <h4 className="text-sm font-semibold text-amber-100">Always blocked without approval</h4>
            <div className="mt-3 space-y-2">
              {(scaling24.always_blocked_without_owner_approval ?? []).slice(0, 8).map((gate) => (
                <p key={gate} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                  {formatLabel(gate)}
                </p>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="specialized-knowledge-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Specialized bot knowledge</p>
            <h3 id="specialized-knowledge-heading" className="mt-1 text-lg font-semibold text-white">
              Every bot gets its own source-backed knowledge system
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{knowledge.mission}</p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {specializedKnowledgeStatus} · {formatDateTime(knowledge.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Profiles', knowledgeSummary.knowledge_profiles],
            ['Domains', knowledgeSummary.knowledge_domains],
            ['All domains', knowledgeSummary.bots_with_all_knowledge_domains],
            ['Source policy', knowledgeSummary.bots_with_source_policy],
            ['Memory policy', knowledgeSummary.bots_with_memory_policy],
            ['Runtime knowledge', knowledgeSummary.bots_with_runtime_tooling_knowledge],
            ['Safety knowledge', knowledgeSummary.bots_with_safety_approval_knowledge],
            ['App knowledge', knowledgeSummary.bots_with_app_builder_knowledge],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Knowledge domains</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(knowledge.knowledge_domains ?? []).slice(0, 8).map((domain) => (
                <article key={domain.id} className="border border-slate-800 bg-slate-950 p-3">
                  <h5 className="text-sm font-semibold text-white">{domain.label}</h5>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{domain.purpose}</p>
                </article>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">Source policy</h4>
              <div className="mt-3 space-y-3">
                <div>
                  <p className="text-xs font-semibold uppercase text-emerald-300">Allowed</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(knowledge.source_policy?.allowed ?? []).slice(0, 6).map((item) => (
                      <span key={item} className="rounded-full border border-emerald-500/30 px-2 py-1 text-[11px] text-emerald-100">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase text-amber-300">Blocked</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(knowledge.source_policy?.blocked ?? []).slice(0, 5).map((item) => (
                      <span key={item} className="rounded-full border border-amber-500/30 px-2 py-1 text-[11px] text-amber-100">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">Memory tiers</h4>
              <div className="mt-3 space-y-2">
                {(knowledge.memory_tiers ?? []).map((tier) => (
                  <p key={tier.id} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                    <span className="font-semibold text-white">{formatLabel(tier.id)}:</span> {tier.purpose}
                  </p>
                ))}
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h4 className="text-sm font-semibold text-white">Sample specialized knowledge profiles</h4>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
              {formatNumber(knowledgeSummary.bot_count)} bot brains
            </span>
          </div>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {(knowledge.dashboard_sample ?? []).slice(0, 8).map((profile) => (
              <article key={profile.slug} className="border border-slate-800 bg-slate-950 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-lg">{profile.emoji}</p>
                    <h5 className="mt-1 text-sm font-semibold text-white">{profile.name}</h5>
                  </div>
                  <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                    {profile.division}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-slate-400">{profile.target_customer}</p>
                <p className="mt-3 text-xs font-semibold text-dreamco-accent">{profile.app_concept_name}</p>
                <div className="mt-3 space-y-2">
                  {(profile.specialized_study_queue ?? []).slice(0, 2).map((item) => (
                    <p key={item} className="border-l-2 border-slate-700 pl-3 text-xs leading-5 text-slate-300">
                      {item}
                    </p>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="ai-agent-model-library-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Prompt, tool, agent, and model library</p>
            <h3 id="ai-agent-model-library-heading" className="mt-1 text-lg font-semibold text-white">
              Buddy picks the best AI route for every task
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{modelLibrary.mission}</p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {aiAgentModelLibraryStatus} · {formatDateTime(modelLibrary.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Model resources', modelLibrarySummary.model_resources],
            ['Providers', modelLibrarySummary.providers],
            ['Agent types', modelLibrarySummary.agent_types],
            ['Prompt types', modelLibrarySummary.prompt_types],
            ['Tool types', modelLibrarySummary.tool_types],
            ['Task routes', modelLibrarySummary.task_routes],
            ['Bots routed', modelLibrarySummary.bots_with_model_routing],
            ['Approval gated', modelLibrarySummary.approval_gated_resources],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Best task routes</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(modelLibrary.task_routes ?? []).slice(0, 8).map((route) => (
                <article key={route.task_type} className="border border-slate-800 bg-slate-950 p-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <h5 className="text-sm font-semibold text-white">{formatLabel(route.task_type)}</h5>
                    <span className="rounded-full border border-dreamco-accent/40 px-2 py-0.5 text-[11px] font-semibold text-dreamco-accent">
                      {formatLabel(route.primary_resource)}
                    </span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    Fallbacks: {(route.fallback_resources ?? []).slice(0, 3).map(formatLabel).join(', ')}
                  </p>
                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    Evals: {(route.required_evals ?? []).slice(0, 4).map(formatLabel).join(', ')}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-amber-900/70 bg-amber-950/20 p-4">
              <h4 className="text-sm font-semibold text-amber-100">Production rule</h4>
              <p className="mt-3 text-xs leading-5 text-amber-100/80">{modelLibrary.policy?.model_id_rule}</p>
              <p className="mt-3 border-l-2 border-amber-300 pl-3 text-xs leading-5 text-amber-100/80">
                {modelLibrary.policy?.approval_rule}
              </p>
            </div>

            <div className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">Agent harness</h4>
              <div className="mt-3 space-y-3">
                {(modelLibrary.agent_prompt_tool_matrix ?? []).slice(0, 5).map((agent) => (
                  <div key={agent.agent_type} className="border border-slate-800 bg-slate-950 p-3">
                    <h5 className="text-xs font-semibold uppercase text-white">{agent.label}</h5>
                    <p className="mt-2 text-xs leading-5 text-slate-400">
                      Prompts: {(agent.prompt_types ?? []).slice(0, 4).map(formatLabel).join(', ')}
                    </p>
                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      Tools: {(agent.tool_types ?? []).slice(0, 4).map(formatLabel).join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <h4 className="text-sm font-semibold text-white">Model strengths and weaknesses</h4>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {(modelLibrary.model_resources ?? []).slice(0, 8).map((resource) => (
              <article key={resource.id} className="border border-slate-800 bg-slate-950 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h5 className="text-sm font-semibold text-white">{resource.provider}</h5>
                  <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                    {formatLabel(resource.tier)}
                  </span>
                </div>
                <p className="mt-2 text-xs font-semibold leading-5 text-dreamco-accent">{resource.label}</p>
                <p className="mt-2 text-xs leading-5 text-emerald-100/80">
                  Good: {(resource.good_at ?? []).slice(0, 3).join(', ')}
                </p>
                <p className="mt-2 text-xs leading-5 text-amber-100/80">
                  Bad: {(resource.bad_at ?? []).slice(0, 2).join(', ')}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="business-launch-expansion-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Business launch and expansion OS</p>
            <h3 id="business-launch-expansion-heading" className="mt-1 text-lg font-semibold text-white">
              Buddy coordinates everything a business needs to start, improve, or expand
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{businessLaunch.mission}</p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {businessLaunchExpansionStatus} · {formatDateTime(businessLaunch.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Service lanes', businessLaunchSummary.service_lanes_ready],
            ['Sub-agents', businessLaunchSummary.sub_agent_roles_ready],
            ['Client workflows', businessLaunchSummary.client_workflows_ready],
            ['Approval gates', businessLaunchSummary.approval_gates_declared],
            ['Review blocks', businessLaunchSummary.professional_review_blocks],
            ['Deliverables', businessLaunchSummary.deliverables_declared],
            ['Test packets', businessLaunchSummary.lane_test_packets],
            ['Bots covered', businessLaunchSummary.bot_count],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">A-to-Z business service lanes</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(businessLaunch.service_lanes ?? []).slice(0, 10).map((lane) => (
                <article key={lane.id} className="border border-slate-800 bg-slate-950 p-3">
                  <h5 className="text-sm font-semibold text-white">{lane.label}</h5>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{lane.purpose}</p>
                  <p className="mt-3 text-xs leading-5 text-dreamco-accent">
                    Deliverables: {(lane.deliverables ?? []).slice(0, 3).map(formatLabel).join(', ')}
                  </p>
                  <p className="mt-2 border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    Approval: {(lane.approval_gates ?? []).slice(0, 3).map(formatLabel).join(', ')}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-amber-900/70 bg-amber-950/20 p-4">
              <h4 className="text-sm font-semibold text-amber-100">Permission rule</h4>
              <p className="mt-3 text-xs leading-5 text-amber-100/80">
                Default mode: {formatLabel(businessLaunch.permission_model?.default_mode)}
              </p>
              <div className="mt-3 space-y-2">
                {(businessLaunch.permission_model?.client_must_approve ?? []).slice(0, 8).map((gate) => (
                  <p key={gate} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    {formatLabel(gate)}
                  </p>
                ))}
              </div>
            </div>

            <div className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">Custom sub-agent roles</h4>
              <div className="mt-3 space-y-3">
                {(businessLaunch.sub_agent_roles ?? []).slice(0, 6).map((agent) => (
                  <div key={agent.id} className="border border-slate-800 bg-slate-950 p-3">
                    <h5 className="text-xs font-semibold uppercase text-white">{agent.label}</h5>
                    <p className="mt-2 text-xs leading-5 text-emerald-100/80">
                      Can prepare: {(agent.can_prepare ?? []).slice(0, 3).join(', ')}
                    </p>
                    <p className="mt-1 text-xs leading-5 text-amber-100/80">
                      Needs approval: {(agent.cannot_do_without_approval ?? []).slice(0, 2).join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="buddy-commerce-publishing-heading" className={`relative overflow-hidden p-5 ${ROYAL_PANEL_CLASS}`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/70 to-transparent" />
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">Buddy commerce and publishing OS</p>
            <h3 id="buddy-commerce-publishing-heading" className={`mt-1 text-lg font-semibold ${ROYAL_TEXT_CLASS}`}>
              Domains, self-publishing, downloads, tasks, and web money research
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">{commercePublishing.mission}</p>
          </div>
          <span className="rounded-full border border-amber-400/50 bg-amber-950/30 px-3 py-1 text-xs font-semibold text-amber-200">
            {buddyCommercePublishingStatus} · {formatDateTime(commercePublishing.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-amber-500/20 bg-amber-500/20 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Score', commercePublishingSummary.readiness_score],
            ['Lanes', commercePublishingSummary.commerce_lanes],
            ['Downloads', commercePublishingSummary.download_targets],
            ['Stores', commercePublishingSummary.app_store_targets],
            ['Task layers', commercePublishingSummary.task_manager_layers],
            ['Categories', commercePublishingSummary.app_categories],
            ['Safe actions', commercePublishingSummary.safe_actions],
            ['Blocked live', commercePublishingSummary.live_actions_blocked],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-950/90 p-4">
              <p className="text-xl font-black text-amber-100">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-950 p-4">
            <h4 className="text-sm font-semibold text-white">Buddy commerce lanes</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(commercePublishing.commerce_lanes ?? []).map((lane) => (
                <article key={lane.id} className="border border-slate-800 bg-slate-900 p-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <h5 className="text-sm font-semibold text-white">{lane.label}</h5>
                    <span className="rounded-full border border-emerald-400/30 px-2 py-0.5 text-[11px] font-semibold text-emerald-100">
                      {formatLabel(lane.dashboard_status)}
                    </span>
                  </div>
                  <p className="mt-3 text-xs leading-5 text-emerald-100/80">
                    Safe: {(lane.safe_actions ?? []).slice(0, 4).join(', ')}
                  </p>
                  <p className="mt-2 border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    Approval: {(lane.approval_required ?? []).slice(0, 4).map(formatLabel).join(', ')}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-amber-900/70 bg-amber-950/20 p-4">
              <h4 className="text-sm font-semibold text-amber-100">Commerce approval wall</h4>
              <div className="mt-3 space-y-2">
                {(commercePublishing.approval_wall ?? []).slice(0, 9).map((gate) => (
                  <p key={gate} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    {formatLabel(gate)}
                  </p>
                ))}
              </div>
            </div>

            <div className="border border-slate-800 bg-slate-950 p-4">
              <h4 className="text-sm font-semibold text-white">Task manager layers</h4>
              <div className="mt-3 flex flex-wrap gap-2">
                {(commercePublishing.task_manager_layers ?? []).slice(0, 10).map((layer) => (
                  <span key={layer} className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300">
                    {formatLabel(layer)}
                  </span>
                ))}
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-2">
          <div className="border border-slate-800 bg-slate-950 p-4">
            <h4 className="text-sm font-semibold text-white">Download and install targets</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(commercePublishing.download_targets ?? []).map((target) => (
                <article key={target.id} className="border border-slate-800 bg-slate-900 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h5 className="text-sm font-semibold text-white">{target.label}</h5>
                    <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                      {formatLabel(target.status)}
                    </span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{target.goal}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="border border-slate-800 bg-slate-950 p-4">
            <h4 className="text-sm font-semibold text-white">App-store and public release packets</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(commercePublishing.app_store_targets ?? []).map((target) => (
                <article key={target.id} className="border border-slate-800 bg-slate-900 p-3">
                  <h5 className="text-sm font-semibold text-white">{target.label}</h5>
                  <p className="mt-2 text-xs leading-5 text-amber-100/80">
                    Needs approval: {(target.approval_required ?? []).slice(0, 3).map(formatLabel).join(', ')}
                  </p>
                </article>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-5 border border-emerald-500/30 bg-emerald-950/20 p-4">
          <h4 className="text-sm font-semibold text-emerald-100">Web money research policy</h4>
          <div className="mt-3 grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-xs font-semibold uppercase text-emerald-200">Allowed sources</p>
              <p className="mt-2 text-xs leading-5 text-emerald-100/80">
                {(commercePublishing.web_research_policy?.allowed_sources ?? []).slice(0, 5).join(', ')}
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-amber-200">Blocked sources</p>
              <p className="mt-2 text-xs leading-5 text-amber-100/80">
                {(commercePublishing.web_research_policy?.blocked_sources ?? []).slice(0, 4).join(', ')}
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-slate-200">Must store</p>
              <p className="mt-2 text-xs leading-5 text-slate-300">
                {(commercePublishing.web_research_policy?.must_store ?? []).slice(0, 6).map(formatLabel).join(', ')}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section aria-labelledby="bot-contract-discovery-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Always-on contract discovery</p>
            <h3 id="bot-contract-discovery-heading" className="mt-1 text-lg font-semibold text-white">
              Every bot searches for contracts and opportunity paths
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{contractDiscovery.mission}</p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {botContractDiscoveryStatus} · {formatDateTime(contractDiscovery.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Bots searching', contractDiscoverySummary.bots_with_contract_discovery],
            ['Opportunity types', contractDiscoverySummary.opportunity_types_tracked],
            ['Source categories', contractDiscoverySummary.source_categories_tracked],
            ['Approval gates', contractDiscoverySummary.approval_gates_declared],
            ['Blocked actions', contractDiscoverySummary.blocked_actions_declared],
            ['Match fields', contractDiscoverySummary.matching_fields],
            ['Scout roles', contractDiscoverySummary.bot_contract_roles],
            ['Samples ready', contractDiscoverySummary.sample_opportunities_ready],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Contract opportunity types</h4>
            <div className="mt-3 flex flex-wrap gap-2">
              {(contractDiscovery.opportunity_types ?? []).map((type) => (
                <span key={type} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
                  {formatLabel(type)}
                </span>
              ))}
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {(contractDiscovery.source_categories ?? []).slice(0, 4).map((source) => (
                <article key={source.id} className="border border-slate-800 bg-slate-950 p-3">
                  <h5 className="text-sm font-semibold text-white">{source.label}</h5>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    Examples: {(source.examples ?? []).slice(0, 3).join(', ')}
                  </p>
                  <p className="mt-2 text-xs leading-5 text-dreamco-accent">
                    Allowed: {(source.allowed_actions ?? []).slice(0, 4).map(formatLabel).join(', ')}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-amber-900/70 bg-amber-950/20 p-4">
              <h4 className="text-sm font-semibold text-amber-100">Approval wall</h4>
              <p className="mt-3 text-xs leading-5 text-amber-100/80">
                Default mode: {formatLabel(contractDiscovery.default_mode)}
              </p>
              <div className="mt-3 space-y-2">
                {(contractDiscovery.approval_gates ?? []).slice(0, 8).map((gate) => (
                  <p key={gate} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    {formatLabel(gate)}
                  </p>
                ))}
              </div>
            </div>

            <div className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">Top opportunity coverage</h4>
              <div className="mt-3 space-y-2">
                {(contractDiscovery.top_opportunity_types ?? []).slice(0, 6).map((item) => (
                  <div key={item.opportunity_type} className="flex items-center justify-between gap-3 border border-slate-800 bg-slate-950 px-3 py-2">
                    <span className="text-xs text-slate-300">{formatLabel(item.opportunity_type)}</span>
                    <span className="text-xs font-semibold text-white">{formatNumber(item.bot_count)}</span>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <h4 className="text-sm font-semibold text-white">Sample bot contract scouts</h4>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {(contractDiscovery.dashboard_sample ?? []).slice(0, 8).map((packet) => (
              <article key={packet.slug} className="border border-slate-800 bg-slate-950 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h5 className="text-sm font-semibold text-white">{packet.name}</h5>
                  <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                    {packet.division}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-slate-400">{packet.sample_search_prompt}</p>
                <p className="mt-3 text-xs leading-5 text-dreamco-accent">
                  {(packet.opportunity_types ?? []).slice(0, 3).map(formatLabel).join(', ')}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="ai-data-package-library-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">AI data package library</p>
            <h3 id="ai-data-package-library-heading" className="mt-1 text-lg font-semibold text-white">
              Rights-cleared data products for model training and evals
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{dataPackageLibrary.mission}</p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {aiDataPackageLibraryStatus} · {formatDateTime(dataPackageLibrary.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Bot blueprints', dataPackageSummary.bot_package_blueprints],
            ['Package types', dataPackageSummary.package_types_ready],
            ['Quality gates', dataPackageSummary.quality_gates_ready],
            ['Commercial models', dataPackageSummary.commercial_models_ready],
            ['Rights fields', dataPackageSummary.required_rights_metadata],
            ['Blocked sources', dataPackageSummary.blocked_source_types],
            ['LangChain packages', dataPackageSummary.langchain_packages],
            ['Samples ready', dataPackageSummary.sellable_package_samples],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Sellable data package types</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(dataPackageLibrary.package_types ?? []).slice(0, 8).map((item) => (
                <article key={item.id} className="border border-slate-800 bg-slate-950 p-3">
                  <h5 className="text-sm font-semibold text-white">{item.label}</h5>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{item.buyer_use}</p>
                  <p className="mt-2 text-xs leading-5 text-dreamco-accent">
                    Formats: {(item.formats ?? []).join(', ')}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-emerald-900/70 bg-emerald-950/20 p-4">
              <h4 className="text-sm font-semibold text-emerald-100">LangChain ready</h4>
              <p className="mt-3 text-xs leading-5 text-emerald-100/80">
                Packages: {(dataPackageLibrary.langchain?.javascript_packages ?? []).join(', ')}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {(dataPackageLibrary.langchain?.use_cases ?? []).slice(0, 6).map((useCase) => (
                  <span key={useCase} className="rounded-full border border-emerald-500/30 px-2 py-1 text-[11px] text-emerald-100">
                    {useCase}
                  </span>
                ))}
              </div>
            </div>

            <div className="border border-amber-900/70 bg-amber-950/20 p-4">
              <h4 className="text-sm font-semibold text-amber-100">Approval gates</h4>
              <div className="mt-3 space-y-2">
                {(dataPackageLibrary.approval_gates ?? []).slice(0, 8).map((gate) => (
                  <p key={gate} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    {formatLabel(gate)}
                  </p>
                ))}
              </div>
            </div>

            <div className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">Quality gates</h4>
              <div className="mt-3 flex flex-wrap gap-2">
                {(dataPackageLibrary.quality_gates ?? []).slice(0, 10).map((gate) => (
                  <span key={gate} className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300">
                    {formatLabel(gate)}
                  </span>
                ))}
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <h4 className="text-sm font-semibold text-white">Sample bot data products</h4>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {(dataPackageLibrary.dashboard_sample ?? []).slice(0, 8).map((packet) => (
              <article key={packet.slug} className="border border-slate-800 bg-slate-950 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h5 className="text-sm font-semibold text-white">{packet.sample_package_name}</h5>
                  <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                    {packet.division}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-slate-400">{packet.sample_buyer_use}</p>
                <p className="mt-3 text-xs leading-5 text-dreamco-accent">
                  {(packet.package_types ?? []).slice(0, 3).map(formatLabel).join(', ')}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="people-job-qualification-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">People search and job qualification</p>
            <h3 id="people-job-qualification-heading" className="mt-1 text-lg font-semibold text-white">
              Buddy prepares privacy-safe people and role-fit lookup packets
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{peopleLookup.mission}</p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {peopleJobQualificationStatus} · {formatDateTime(peopleLookup.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Bot blueprints', peopleLookupSummary.bot_people_lookup_blueprints],
            ['Lookup lanes', peopleLookupSummary.qualification_lanes_ready],
            ['Approval gates', peopleLookupSummary.approval_gates_declared],
            ['Blocked uses', peopleLookupSummary.blocked_uses_declared],
            ['Allowed sources', peopleLookupSummary.allowed_source_types],
            ['Blocked sources', peopleLookupSummary.blocked_source_types],
            ['Privacy fields', peopleLookupSummary.privacy_metadata_fields],
            ['Human review', peopleLookupSummary.human_review_required ? 'Yes' : 'No'],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{typeof value === 'number' ? formatNumber(value) : value}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Qualification lookup lanes</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(peopleLookup.qualification_lanes ?? []).slice(0, 6).map((lane) => (
                <article key={lane.id} className="border border-slate-800 bg-slate-950 p-3">
                  <h5 className="text-sm font-semibold text-white">{lane.label}</h5>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{lane.purpose}</p>
                  <p className="mt-2 text-xs leading-5 text-dreamco-accent">
                    Outputs: {(lane.outputs ?? []).slice(0, 3).map(formatLabel).join(', ')}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-emerald-900/70 bg-emerald-950/20 p-4">
              <h4 className="text-sm font-semibold text-emerald-100">Allowed sources</h4>
              <div className="mt-3 flex flex-wrap gap-2">
                {(peopleLookup.privacy_policy?.allowed_sources ?? []).slice(0, 8).map((source) => (
                  <span key={source} className="rounded-full border border-emerald-500/30 px-2 py-1 text-[11px] text-emerald-100">
                    {source}
                  </span>
                ))}
              </div>
            </div>

            <div className="border border-amber-900/70 bg-amber-950/20 p-4">
              <h4 className="text-sm font-semibold text-amber-100">Approval and blocked uses</h4>
              <div className="mt-3 space-y-2">
                {(peopleLookup.approval_gates ?? []).slice(0, 7).map((gate) => (
                  <p key={gate} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    {formatLabel(gate)}
                  </p>
                ))}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {(peopleLookup.blocked_uses ?? []).slice(0, 5).map((blocked) => (
                  <span key={blocked} className="rounded-full border border-red-500/30 px-2 py-1 text-[11px] text-red-100">
                    {formatLabel(blocked)}
                  </span>
                ))}
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <h4 className="text-sm font-semibold text-white">Sample people lookup bot packets</h4>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {(peopleLookup.dashboard_sample ?? []).slice(0, 8).map((packet) => (
              <article key={packet.slug} className="border border-slate-800 bg-slate-950 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h5 className="text-sm font-semibold text-white">{packet.name}</h5>
                  <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                    {packet.division}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-slate-400">{packet.sample_lookup_prompt}</p>
                <p className="mt-3 text-xs leading-5 text-dreamco-accent">
                  {(packet.qualification_lanes ?? []).slice(0, 3).map(formatLabel).join(', ')}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="bot-owner-settings-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Actions page settings</p>
            <h3 id="bot-owner-settings-heading" className="mt-1 text-lg font-semibold text-white">
              Every bot is a business owner with permission switches
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{ownerSettings.mission}</p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {botOwnerSettingsStatus} · {formatDateTime(ownerSettings.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Owner bots', ownerSettingsSummary.bots_with_owner_settings],
            ['Business mode', ownerSettingsSummary.business_owner_enabled_bots],
            ['Safe mode', ownerSettingsSummary.safe_mode_enabled_bots],
            ['High risk', ownerSettingsSummary.high_risk_bots],
            ['Safe-unblocked', ownerSettingsSummary.high_risk_bots_unblocked_for_safe_work],
            ['Approval required', ownerSettingsSummary.live_action_approval_required_bots],
            ['Controls', ownerSettingsSummary.settings_controls_ready],
            ['Guardrails', ownerSettingsSummary.guardrails_ready],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Global settings buttons</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {(ownerSettings.global_settings ?? []).slice(0, 12).map((setting) => (
                <button
                  key={setting.id}
                  type="button"
                  className={`border p-3 text-left ${
                    setting.default
                      ? 'border-emerald-500/40 bg-emerald-950/20 text-emerald-100'
                      : 'border-amber-500/40 bg-amber-950/20 text-amber-100'
                  }`}
                  aria-pressed={Boolean(setting.default)}
                >
                  <span className="block text-sm font-semibold">{setting.label}</span>
                  <span className="mt-1 block text-[11px] font-bold uppercase">
                    {setting.default ? 'On by default' : 'Approval only'}
                  </span>
                  <span className="mt-2 block text-xs leading-5 text-slate-300">{setting.description}</span>
                </button>
              ))}
            </div>
          </div>

          <aside className="space-y-5">
            <div className="border border-amber-900/70 bg-amber-950/20 p-4">
              <h4 className="text-sm font-semibold text-amber-100">Approval-only guardrails</h4>
              <div className="mt-3 space-y-2">
                {(ownerSettings.always_require_approval ?? []).slice(0, 10).map((gate) => (
                  <p key={gate} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    {formatLabel(gate)}
                  </p>
                ))}
              </div>
            </div>

            <div className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">Permission groups</h4>
              <div className="mt-3 space-y-3">
                {(ownerSettings.permission_groups ?? []).slice(0, 5).map((group) => (
                  <div key={group.id} className="border border-slate-800 bg-slate-950 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <h5 className="text-xs font-semibold uppercase text-white">{group.label}</h5>
                      <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${group.default ? 'border-emerald-500/40 text-emerald-200' : 'border-amber-500/40 text-amber-200'}`}>
                        {group.default ? 'on' : 'approval'}
                      </span>
                    </div>
                    <p className="mt-2 text-xs leading-5 text-slate-400">
                      {(group.permissions ?? []).slice(0, 5).map(formatLabel).join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Sample bot owner controls</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              {(ownerSettings.dashboard_sample ?? []).slice(0, 8).map((bot) => (
                <article key={bot.slug} className="border border-slate-800 bg-slate-950 p-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <h5 className="text-sm font-semibold text-white">{bot.name}</h5>
                    <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase ${bot.risk_hint === 'high' ? 'border-amber-500/40 text-amber-200' : 'border-emerald-500/40 text-emerald-200'}`}>
                      {bot.risk_hint}
                    </span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{bot.division}</p>
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    {Object.entries(bot.controls ?? {}).slice(0, 6).map(([control, enabled]) => (
                      <button
                        key={control}
                        type="button"
                        aria-pressed={Boolean(enabled)}
                        className={`border px-2 py-1 text-left text-[11px] font-semibold ${enabled ? 'border-emerald-500/40 text-emerald-200' : 'border-slate-700 text-slate-400'}`}
                      >
                        {formatLabel(control)}
                      </button>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </div>

          <aside className="border border-emerald-900/70 bg-emerald-950/20 p-4">
            <h4 className="text-sm font-semibold text-emerald-100">Guardrails</h4>
            <div className="mt-3 space-y-2">
              {(ownerSettings.guardrails ?? []).slice(0, 8).map((guardrail) => (
                <p key={guardrail} className="border-l-2 border-emerald-400 pl-3 text-xs leading-5 text-emerald-100/80">
                  {guardrail}
                </p>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="competitive-roadmap-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Competitive build roadmap</p>
            <h3 id="competitive-roadmap-heading" className="mt-1 text-lg font-semibold text-white">
              What Buddy needs to beat ordinary vibe coding
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              These are the product capabilities Buddy tracks so every client build can move toward live preview,
              deployment, rollback, media input, and a test loop after every generated change.
            </p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {COMPETITIVE_BUILD_ROADMAP.length} capabilities tracked
          </span>
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-3">
          {COMPETITIVE_BUILD_ROADMAP.map((item) => (
            <article key={item.capability} className="min-h-44 bg-slate-900 p-4">
              <div className="flex items-start justify-between gap-3">
                <h4 className="text-sm font-semibold text-white">{item.capability}</h4>
                <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase ${
                  item.status === 'building'
                    ? 'border-green-800 bg-green-950/30 text-green-300'
                    : 'border-slate-700 bg-slate-950 text-slate-300'
                }`}>
                  {item.status}
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-slate-400">{item.proof}</p>
            </article>
          ))}
        </div>
      </section>

      <section aria-labelledby="best-path-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Best path to compete</p>
            <h3 id="best-path-heading" className="mt-1 text-lg font-semibold text-white">
              Trust-first AI company builder roadmap
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Buddy should compete by turning prompts into governed businesses, bot workers, creative systems,
              evidence, and client-ready delivery instead of stopping at generated code.
            </p>
          </div>
          <span className="rounded-full border border-green-800 bg-green-950/30 px-3 py-1 text-xs font-semibold text-green-300">
            safest path · strongest lane
          </span>
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-2 xl:grid-cols-3">
          {BEST_COMPETITIVE_PATH.map((step) => (
            <article key={step.phase} className="min-h-56 bg-slate-900 p-4">
              <div className="flex items-start justify-between gap-3">
                <span className="font-mono text-xs text-dreamco-accent">{step.phase}</span>
                <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-400">
                  {step.timeframe}
                </span>
              </div>
              <h4 className="mt-3 text-sm font-semibold text-white">{step.title}</h4>
              <p className="mt-2 text-xs leading-5 text-slate-400">{step.focus}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {step.proof.map((item) => (
                  <span key={item} className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300">
                    {item}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section aria-labelledby="trust-layer-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Buddy Trust Layer</p>
            <h3 id="trust-layer-heading" className="mt-1 text-lg font-semibold text-white">
              AI company builder with human trust built in
            </h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              DreamCo can present every bot as an AI company, department, or employee.
              Buddy is the face of trust: evidence first, approvals visible, and risky live actions blocked until the owner authorizes them.
            </p>
            <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-4">
              {COMPANY_BUILDER_PILLARS.map((pillar) => (
                <div key={pillar.title} className="min-h-36 bg-slate-900 p-4">
                  <h4 className="text-sm font-semibold text-white">{pillar.title}</h4>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{pillar.detail}</p>
                </div>
              ))}
            </div>
          </div>
          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Trust scorecard</h4>
            <div className="mt-3 space-y-3">
              {[
                ['Runtime coverage', inventorySummary.all_bots_have_executable_runtime ? 'Complete' : 'In progress'],
                ['System libraries', inventorySummary.all_system_libraries_cover_profiled_bots ? 'Complete' : 'In progress'],
                ['Production-ready', `${formatNumber(inventorySummary.production_ready_bots)} bots`],
                ['Approval-gated', `${formatNumber(inventorySummary.buddy_money_approval_required_bots ?? productionStates.production_candidate_approval_required)} bots`],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between gap-3 border-b border-slate-800 pb-2">
                  <span className="text-xs uppercase text-slate-500">{label}</span>
                  <span className="text-sm font-semibold text-white">{value}</span>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              Buddy can keep building and learning continuously through reports, pull requests, sandbox tests, and approval workflows.
            </p>
          </aside>
        </div>
      </section>

      <section aria-labelledby="productivity-tracker-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Buddy Productivity Tracker</p>
            <h3 id="productivity-tracker-heading" className="mt-1 text-lg font-semibold text-white">
              Tracks what helps you, clients, and bots improve
            </h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Buddy combines bot readiness, repository cleanup, workflow health, cost savings, and client demo readiness
              into one productivity map with next actions.
            </p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {buddyProductivityStatus} · {formatDateTime(productivity.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Score', productivitySummary.productivity_score],
            ['Bots tracked', productivitySummary.bot_count],
            ['Runtime ready', productivitySummary.runtime_ready_bots],
            ['Production ready', productivitySummary.production_ready_bots],
            ['Approval gated', productivitySummary.approval_gated_bots],
            ['Open PRs', productivitySummary.open_prs],
            ['Open issues', productivitySummary.open_issues],
            ['Monthly savings', `$${formatNumber(productivitySummary.estimated_monthly_savings_usd)}`],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{typeof value === 'number' ? formatNumber(value) : value}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-3">
          {[
            ['For you', productivity.owner_productivity?.tracks ?? [], productivity.owner_productivity?.current_focus ?? []],
            ['For clients', productivity.client_productivity?.tracks ?? [], productivity.client_productivity?.ready_to_show ?? []],
            ['For bots', productivity.bot_productivity?.tracks ?? [], productivity.next_actions ?? []],
          ].map(([title, tracks, focus]) => (
            <div key={title} className="border border-slate-800 bg-slate-900 p-4">
              <h4 className="text-sm font-semibold text-white">{title}</h4>
              <div className="mt-3 flex flex-wrap gap-2">
                {tracks.slice(0, 6).map((item) => (
                  <span key={item} className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300">
                    {formatLabel(item)}
                  </span>
                ))}
              </div>
              <div className="mt-4 space-y-2">
                {focus.slice(0, 3).map((item) => (
                  <p key={item} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-400">
                    {item}
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_22rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Learning loops Buddy watches</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(productivity.learning_loops ?? []).slice(0, 4).map((loop) => (
                <div key={loop.name} className="border border-slate-800 bg-slate-950 p-3">
                  <p className="text-sm font-semibold text-white">{loop.name}</p>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{loop.helps}</p>
                </div>
              ))}
            </div>
          </div>
          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Bot learning coverage</h4>
            <div className="mt-3 space-y-3">
              {[
                ['Runtime ready', productivity.bot_productivity?.coverage?.runtime_ready_percent],
                ['Production ready', productivity.bot_productivity?.coverage?.production_ready_percent],
                ['Approval gated', productivity.bot_productivity?.coverage?.approval_gated_percent],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between gap-3 border-b border-slate-800 pb-2">
                  <span className="text-xs uppercase text-slate-500">{label}</span>
                  <span className="text-sm font-semibold text-white">{formatNumber(value)}%</span>
                </div>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="buddy-tracker-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Always-on repository scan</p>
            <h3 id="buddy-tracker-heading" className="mt-1 text-lg font-semibold text-white">🤝 Buddy capability tracker</h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Tracks what Buddy can do, what is built, what is ready for testing, and what still needs implementation.
            </p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {buddyInventoryStatus} · {formatDateTime(inventory.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-6">
          {[
            ['Bot profiles', inventorySummary.bot_profiles_scanned],
            ['Test files', inventorySummary.test_files],
            ['Workflows', inventorySummary.workflows],
            ['Buddy systems', inventorySummary.buddy_related_bots],
            ['Ready test runs', testStates.ready_for_test_run],
            ['Coding paths', inventorySummary.bots_with_full_coding_path],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_22rem]">
          <div>
            <h4 className="text-sm font-semibold text-white">Build and test states</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-3">
              <div className="border border-green-800 bg-green-950/20 p-4">
                <p className="text-2xl font-black text-green-300">{formatNumber(buildStates.built_and_test_covered)}</p>
                <p className="mt-1 text-xs uppercase text-green-200">Built + test-covered</p>
              </div>
              <div className="border border-dreamco-accent/50 bg-dreamco-accent/10 p-4">
                <p className="text-2xl font-black text-dreamco-accent">{formatNumber(buildStates.built_contract_ready)}</p>
                <p className="mt-1 text-xs uppercase text-slate-300">Contract-ready</p>
              </div>
              <div className="border border-yellow-800 bg-yellow-950/20 p-4">
                <p className="text-2xl font-black text-yellow-300">{formatNumber(inventorySummary.placeholder_marker_bots)}</p>
                <p className="mt-1 text-xs uppercase text-yellow-100">Review markers</p>
              </div>
            </div>

            <div className="mt-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-sm font-semibold text-white">Path to fully coded</h4>
                <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                  inventorySummary.all_bots_have_full_coding_path
                    ? 'border-green-800 bg-green-950/30 text-green-300'
                    : 'border-yellow-800 bg-yellow-950/30 text-yellow-300'
                }`}>
                  {inventorySummary.all_bots_have_full_coding_path ? 'All bots have a path' : 'Path gaps found'}
                </span>
              </div>
              <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-5">
                {[
                  ['On full path', codingPathStates.on_full_code_path],
                  ['Review placeholders', codingPathStates.needs_placeholder_review],
                  ['Add direct tests', codingPathStates.needs_direct_test_coverage],
                  ['Build core files', codingPathStates.needs_core_implementation],
                  ['Map systems', codingPathStates.needs_existing_system_mapping],
                ].map(([label, value]) => (
                  <div key={label} className="border border-slate-800 bg-slate-900 p-3">
                    <p className="text-lg font-black text-white">{formatNumber(value)}</p>
                    <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-sm font-semibold text-white">Production readiness</h4>
                <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                  inventorySummary.all_bots_production_ready
                    ? 'border-green-800 bg-green-950/30 text-green-300'
                    : 'border-yellow-800 bg-yellow-950/30 text-yellow-300'
                }`}>
                  {inventorySummary.all_bots_production_ready ? 'All bots production-ready' : 'Review gates active'}
                </span>
              </div>
              <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-5">
                {[
                  ['Production ready', inventorySummary.production_ready_bots],
                  ['Fully coded', inventorySummary.fully_coded_bots],
                  ['Approval needed', productionStates.production_candidate_approval_required],
                  ['Needs tests', productionStates.not_ready_needs_tests],
                  ['Needs implementation', productionStates.not_ready_missing_implementation],
                ].map(([label, value]) => (
                  <div key={label} className="border border-slate-800 bg-slate-900 p-3">
                    <p className="text-lg font-black text-white">{formatNumber(value)}</p>
                    <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-5 border border-amber-800 bg-amber-950/20 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h4 className="text-sm font-semibold text-amber-100">Final live-action approval gate</h4>
                  <p className="mt-1 max-w-3xl text-xs leading-5 text-amber-100/80">
                    All bots can run in sandbox mode after green smoke tests. High-risk money, trading, legal, medical,
                    tax, security, and third-party actions stay blocked until Buddy records owner-approved live actions.
                  </p>
                </div>
                <span className="rounded-full border border-amber-500/50 px-3 py-1 text-xs font-semibold text-amber-200">
                  {productionApprovalPacketsStatus} · {formatDateTime(approvalPackets.generated_at)}
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-px overflow-hidden border border-amber-900 bg-amber-900 md:grid-cols-4 xl:grid-cols-6">
                {[
                  ['Approval packets', approvalPacketSummary.approval_packets],
                  ['Live approved', approvalPacketSummary.live_approved],
                  ['Approval required', approvalPacketSummary.approval_required],
                  ['Smoke passed', approvalPacketSummary.smoke_tests_passed],
                  ['Smoke failed', approvalPacketSummary.smoke_tests_failed],
                  ['Sandbox candidates', approvalPacketSummary.sandbox_safe_production_candidates],
                ].map(([label, value]) => (
                  <div key={label} className="bg-slate-950 p-3">
                    <p className="text-lg font-black text-white">{formatNumber(value)}</p>
                    <p className="mt-1 text-xs uppercase text-amber-100/70">{label}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
                <div className="border border-amber-900/70 bg-slate-950 p-3">
                  <p className="text-xs font-semibold uppercase text-amber-200">Required owner phrase</p>
                  <p className="mt-2 text-sm leading-6 text-white">{approvalPackets.required_buddy_money_request}</p>
                </div>
                <div className="border border-amber-900/70 bg-slate-950 p-3">
                  <p className="text-xs font-semibold uppercase text-amber-200">Top risk groups</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {Object.entries(approvalPackets.risk_breakdown ?? {}).slice(0, 6).map(([risk, count]) => (
                      <span key={risk} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
                        {formatLabel(risk)}: {formatNumber(count)}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-4 grid gap-3 lg:grid-cols-3">
                {(approvalPackets.next_actions ?? []).slice(0, 3).map((action) => (
                  <p key={action} className="border-l-2 border-amber-400 pl-3 text-xs leading-5 text-amber-100/80">
                    {action}
                  </p>
                ))}
              </div>
            </div>

            <div className="mt-5">
              <h4 className="text-sm font-semibold text-white">Direct Buddy systems</h4>
              <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                {directBuddyBots.slice(0, 9).map((bot) => (
                  <div key={bot.slug} className="border border-slate-800 bg-slate-900 p-3">
                    <p className="truncate text-sm font-semibold text-white">{bot.name}</p>
                    <p className="mt-1 text-xs text-slate-500">{formatLabel(bot.test_state)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Needs implementation before testing</h4>
            <div className="mt-3 space-y-2">
              {needsImplementation.length > 0 ? (
                needsImplementation.slice(0, 8).map((bot) => (
                  <div key={bot.slug} className="border-l-2 border-yellow-500 pl-3">
                    <p className="text-sm font-semibold text-white">{bot.name}</p>
                    <p className="text-xs text-slate-500">{bot.division} · {bot.slug}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-green-300">No implementation blockers found.</p>
              )}
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              Next queues: {formatNumber(needsDirectTests.length)} need direct test promotion and {formatNumber(needsSystemMapping.length)} need system mapping.
              Review markers are conservative: they flag placeholder-like text for human review, not automatic failure.
            </p>
          </aside>
        </div>
      </section>

      <section aria-labelledby="bot-test-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Sandbox bot testing</p>
            <h3 id="bot-test-heading" className="mt-1 text-lg font-semibold text-white">🧪 Buddy and bot test catalog</h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Search every registered bot, see what it can do for you, your users, and Buddy, then prepare a safe sandbox test packet.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => prepareBotTest(botCatalog.find((bot) => bot.slug === 'buddy-bot') ?? selectedBot, 'buddy')}
              className="rounded-md bg-dreamco-accent px-3 py-2 text-sm font-semibold text-white hover:bg-dreamco-accent/80"
            >
              Test Buddy
            </button>
            <button
              type="button"
              onClick={() => prepareBotTest(selectedBot)}
              className="rounded-md border border-slate-600 px-3 py-2 text-sm font-semibold text-slate-200 hover:border-slate-400"
            >
              Test selected bot
            </button>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-5">
          {[
            ['Catalog bots', botCatalog.length],
            ['Executable runtimes', inventorySummary.executable_runtime_ready_bots],
            ['Sandbox ready', testStates.ready_for_test_run],
            ['Production ready', inventorySummary.production_ready_bots],
            ['Approval gated', inventorySummary.buddy_money_approval_required_bots ?? productionStates.production_candidate_approval_required],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-white">Buddy all-bot connection proof</h4>
              <p className="mt-1 text-xs leading-5 text-slate-400">
                Verifies every bot can be routed by Buddy, tested from this Actions page, and backed by customized resources.
              </p>
            </div>
            <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
              buddyConnectionSummary.all_bots_ready
                ? 'border-green-800 bg-green-950/40 text-green-300'
                : 'border-yellow-800 bg-yellow-950/40 text-yellow-300'
            }`}>
              {buddyBotConnectionsStatus} · {buddyConnectionSummary.all_bots_ready ? 'all connected' : 'needs attention'}
            </span>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-5">
            {[
              ['Buddy-connected', buddyConnectionSummary.buddy_connected_bots],
              ['Actions-testable', buddyConnectionSummary.actions_page_testable_bots],
              ['Custom resources', buddyConnectionSummary.custom_resource_ready_bots],
              ['Resources per bot', buddyConnectionSummary.resources_per_bot_required],
              ['Failures', buddyConnectionSummary.failed_bots],
            ].map(([label, value]) => (
              <div key={label} className="bg-slate-950 p-3">
                <p className="text-lg font-black text-white">{formatNumber(value)}</p>
                <p className="mt-1 text-[11px] uppercase text-slate-500">{label}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[20rem_minmax(0,1fr)]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <label htmlFor="bot-search" className="text-sm font-semibold text-white">Find a bot</label>
            <input
              id="bot-search"
              value={botSearch}
              onChange={(event) => setBotSearch(event.target.value)}
              placeholder="Search name, division, capability"
              className="mt-3 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:border-dreamco-accent focus:outline-none"
            />
            <div className="mt-3 max-h-96 space-y-2 overflow-y-auto pr-1">
              {visibleBots.map((bot) => (
                <button
                  key={bot.slug}
                  type="button"
                  onClick={() => {
                    setSelectedBotSlug(bot.slug);
                    setBotTestPacket(null);
                  }}
                  className={`w-full border px-3 py-3 text-left ${
                    selectedBot.slug === bot.slug
                      ? 'border-dreamco-accent bg-dreamco-accent/15'
                      : 'border-slate-800 bg-slate-950 hover:border-slate-600'
                  }`}
                >
                  <span className="block truncate text-sm font-semibold text-white">
                    {String(bot.slug).includes('buddy') ? '🤝 ' : '🤖 '}
                    {bot.name}
                  </span>
                  <span className="mt-1 block text-xs text-slate-500">
                    {bot.division ?? 'DreamCo'} · {formatLabel(bot.test_state)}
                  </span>
                </button>
              ))}
              {visibleBots.length === 0 && (
                <p className="border border-slate-800 bg-slate-950 p-3 text-sm text-slate-400">No bots matched that search.</p>
              )}
            </div>
          </div>

          <div className="border border-slate-800 bg-slate-900 p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase text-slate-500">{selectedBot.division ?? 'DreamCo'} · {selectedBot.slug}</p>
                <h4 className="mt-1 text-xl font-bold text-white">
                  {String(selectedBot.slug).includes('buddy') ? '🤝 ' : '🤖 '}
                  {selectedBot.name}
                </h4>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                  {selectedBot.description || 'This bot is registered in the DreamCo fleet and ready for governed sandbox testing.'}
                </p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                selectedBot.production_ready
                  ? 'border-green-800 bg-green-950/30 text-green-300'
                  : selectedBot.production_readiness_status === 'production_candidate_approval_required'
                    ? 'border-yellow-800 bg-yellow-950/30 text-yellow-300'
                    : 'border-slate-700 bg-slate-950 text-slate-300'
              }`}>
                {formatLabel(selectedBot.production_readiness_status ?? selectedBot.test_state)}
              </span>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <div className="border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs font-semibold uppercase text-dreamco-accent">For you</p>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {selectedBot.description || `${selectedBot.name} helps operate ${selectedBot.division ?? 'DreamCo'} workflows.`}
                </p>
              </div>
              <div className="border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs font-semibold uppercase text-dreamco-accent">For your users</p>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {selectedBotCapabilities.length
                    ? `Users can get ${selectedBotCapabilities.slice(0, 3).join(', ')}.`
                    : 'Users can get governed assistance once this bot has richer capability labels.'}
                </p>
              </div>
              <div className="border border-slate-700 bg-slate-950 p-4">
                <p className="text-xs font-semibold uppercase text-dreamco-accent">For Buddy</p>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  Buddy can route this bot through sandbox tests, inspect {formatNumber(selectedBot.test_count)} test file(s), and keep its {formatLabel(selectedBot.test_state)} state visible.
                </p>
              </div>
            </div>

            <div className="mt-5">
              <h5 className="text-sm font-semibold text-white">Capabilities</h5>
              <div className="mt-3 flex flex-wrap gap-2">
                {selectedBotCapabilities.map((capability) => (
                  <span key={capability} className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300">
                    {capability}
                  </span>
                ))}
                {selectedBotCapabilities.length === 0 && (
                  <span className="text-sm text-slate-400">No capability labels found yet.</span>
                )}
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="border border-slate-700 p-3"><p className="text-xs text-slate-500">Build state</p><p className="mt-1 text-sm text-white">{formatLabel(selectedBot.build_state)}</p></div>
              <div className="border border-slate-700 p-3"><p className="text-xs text-slate-500">Test state</p><p className="mt-1 text-sm text-white">{formatLabel(selectedBot.test_state)}</p></div>
              <div className="border border-slate-700 p-3"><p className="text-xs text-slate-500">Risk gate</p><p className="mt-1 text-sm text-white">{formatLabel(selectedBot.risk_hint ?? 'standard')}</p></div>
            </div>

            <div className="mt-5 border border-slate-800 bg-slate-950 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h5 className="text-sm font-semibold text-white">Buddy test evidence dossier</h5>
                <span className="rounded-full border border-green-800 bg-green-950/30 px-2 py-0.5 text-[11px] font-semibold uppercase text-green-300">
                  Connected
                </span>
              </div>
              <div className="mt-3 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  ['Buddy route', selectedBot.slug],
                  ['Sandbox command', 'run_generated_bot_smoke.py'],
                  ['Custom resources', buddyConnectionSummary.resources_per_bot_required],
                  ['Approval policy', selectedBot.risk_hint === 'high' ? 'Owner required' : 'Sandbox allowed'],
                ].map(([label, value]) => (
                  <div key={label} className="bg-slate-900 p-3">
                    <p className="truncate font-mono text-xs text-white">{value}</p>
                    <p className="mt-1 text-[11px] uppercase text-slate-500">{label}</p>
                  </div>
                ))}
              </div>
            </div>

            {(selectedBot.tests ?? []).length > 0 && (
              <div className="mt-5">
                <h5 className="text-sm font-semibold text-white">Test files</h5>
                <ul className="mt-2 space-y-1 text-xs text-slate-400">
                  {(selectedBot.tests ?? []).slice(0, 5).map((testPath) => (
                    <li key={testPath} className="font-mono">{testPath}</li>
                  ))}
                </ul>
              </div>
            )}

            {botTestPacket && (
              <div role="status" className="mt-5 border border-green-800 bg-green-950/30 p-4 text-sm text-green-300">
                Sandbox test packet prepared for {botTestPacket.name}. Run command: <span className="font-mono">{botTestPacket.command}</span>.
                <span className="mt-1 block text-xs text-green-200">
                  Approval state: {formatLabel(botTestPacket.approval)}. Live money, outreach, and production actions stay blocked from this dashboard.
                </span>
              </div>
            )}
          </div>
        </div>
      </section>

      <section aria-labelledby="repository-cleanroom-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Repository Cleanroom</p>
            <h3 id="repository-cleanroom-heading" className="mt-1 text-lg font-semibold text-white">
              Always-clean PR, issue, and code-quality steward
            </h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Buddy keeps the pull request and issue sections organized by separating ready work, stale work,
              close candidates, retest queues, and syntax gates before anything is presented as safe to merge.
            </p>
          </div>
          <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
            stewardshipSummary.cleanroom_ready
              ? 'border-green-800 bg-green-950/30 text-green-300'
              : 'border-yellow-800 bg-yellow-950/30 text-yellow-300'
          }`}>
            {repositoryStewardshipStatus} · {stewardshipSummary.cleanroom_ready ? 'cleanroom ready' : 'cleanup active'}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Ready PRs', stewardshipSummary.ready_prs],
            ['Stale PRs', stewardshipSummary.stale_prs],
            ['Stale issues', stewardshipSummary.stale_issues],
            ['Close PR plans', stewardshipSummary.planned_close_prs],
            ['Close issue plans', stewardshipSummary.planned_close_issues],
            ['Quality gates', stewardshipSummary.quality_checks],
            ['Failed gates', stewardshipSummary.failed_quality_checks],
            ['Workflow blockers', stewardshipSummary.failed_workflow_runs],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_22rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Safe code quality gates</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-3">
              {(stewardship.quality_checks ?? []).map((check) => (
                <div key={check.name} className="border border-slate-800 bg-slate-950 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-white">{formatLabel(check.name)}</p>
                    <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase ${
                      check.status === 'pass'
                        ? 'border-green-800 bg-green-950/30 text-green-300'
                        : check.status === 'skipped'
                          ? 'border-slate-700 bg-slate-800 text-slate-300'
                          : 'border-yellow-800 bg-yellow-950/30 text-yellow-300'
                    }`}>
                      {check.status}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    {formatNumber(check.scanned)} file(s) scanned · {formatNumber((check.failures ?? []).length)} failure(s)
                  </p>
                  {(check.failures ?? []).slice(0, 2).map((failure) => (
                    <p key={`${check.name}-${failure.file}`} className="mt-2 break-words font-mono text-[11px] text-yellow-200">
                      {failure.file}
                    </p>
                  ))}
                </div>
              ))}
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Cleanup policy</h4>
            <div className="mt-3 space-y-3 text-xs leading-5 text-slate-400">
              <p>Auto-close without owner approval: {String(stewardship.policy?.auto_close_without_owner_approval)}</p>
              <p>Auto-merge without green checks: {String(stewardship.policy?.auto_merge_without_green_checks)}</p>
            </div>
            <div className="mt-4 space-y-2">
              {(stewardship.policy?.required_before_ready ?? []).map((item) => (
                <div key={item} className="border-l-2 border-dreamco-accent pl-3 text-xs text-slate-300">
                  {formatLabel(item)}
                </div>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="debugging-os-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Buddy Debugging OS</p>
            <h3 id="debugging-os-heading" className="mt-1 text-lg font-semibold text-white">
              Sellable debugging system for apps, bots, workflows, and AI builds
            </h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              A repeatable debugging pipeline that captures evidence, reproduces failures, isolates root cause,
              patches safely, verifies tests, and packages the result for pull requests or client handoff.
            </p>
          </div>
          <span className="rounded-full border border-green-800 bg-green-950/30 px-3 py-1 text-xs font-semibold text-green-300">
            client-ready offer
          </span>
        </div>

        <div className="mt-5 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-3">
          {DEBUGGING_OS_STAGES.map((stage, index) => (
            <article key={stage.stage} className="min-h-48 bg-slate-900 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-mono text-xs text-dreamco-accent">0{index + 1}</p>
                  <h4 className="mt-2 text-sm font-semibold text-white">{stage.stage}</h4>
                </div>
                <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-400">
                  debug
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-slate-400">{stage.detail}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {stage.evidence.map((item) => (
                  <span key={item} className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300">
                    {item}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <h4 className="text-sm font-semibold text-white">Sellable debugging packages</h4>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {SELLABLE_DEBUG_PACKAGES.map(([title, detail]) => (
              <div key={title} className="border border-slate-800 bg-slate-950 p-3">
                <p className="text-sm font-semibold text-white">{title}</p>
                <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h4 className="text-sm font-semibold text-white">Debug every Actions and Agents failure</h4>
                <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-400">
                  Buddy combines workflow failures, syntax gates, bot connection issues, storage warnings, and revenue blockers
                  into one repair queue with evidence, route, next action, and retest expectations.
                </p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                failureDebugQueue.length === 0
                  ? 'border-green-800 bg-green-950/30 text-green-300'
                  : 'border-yellow-800 bg-yellow-950/30 text-yellow-300'
              }`}>
                {formatNumber(failureDebugQueue.length)} failure packet(s)
              </span>
            </div>

            <div className="mt-4 space-y-3">
              {failureDebugQueue.map((failure) => (
                <article key={failure.id} className="border border-slate-800 bg-slate-950 p-3">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-[11px] font-bold uppercase text-dreamco-accent">{failure.source}</p>
                      <h5 className="mt-1 text-sm font-semibold text-white">{failure.title}</h5>
                      <p className="mt-1 break-words font-mono text-[11px] text-slate-500">{failure.target}</p>
                    </div>
                    <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-slate-300">
                      {failure.route}
                    </span>
                  </div>
                  <p className="mt-3 text-xs leading-5 text-yellow-100">{failure.evidence}</p>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{failure.action}</p>
                </article>
              ))}
              {failureDebugQueue.length === 0 && (
                <p className="border border-green-800 bg-green-950/20 p-3 text-sm text-green-300">
                  No active failure packets found. Buddy stays ready to capture the next failing check, agent, workflow, or integration.
                </p>
              )}
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Failure routing playbook</h4>
            <div className="mt-3 space-y-3">
              {FAILURE_DEBUG_ROUTES.map(([title, detail]) => (
                <div key={title} className="border-l-2 border-dreamco-accent pl-3">
                  <p className="text-xs font-semibold text-white">{title}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{detail}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 border border-slate-800 bg-slate-950 p-3">
              <h5 className="text-xs font-semibold uppercase text-slate-300">Perfect-debug gates</h5>
              <div className="mt-3 space-y-2">
                {FAILURE_DEBUG_GATES.map((gate) => (
                  <p key={gate} className="text-xs leading-5 text-slate-400">{gate}</p>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section aria-labelledby="stripe-rescue-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Stripe revenue rescue</p>
            <h3 id="stripe-rescue-heading" className="mt-1 text-lg font-semibold text-white">
              Fix why connected Stripe is making no money
            </h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Checks whether offers are live, customer buttons reach verified payment links, webhook events are arriving,
              and successful payments or invoices are actually tracked.
            </p>
          </div>
          <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
            stripeRescueSummary.revenue_rescue_ready
              ? 'border-green-800 bg-green-950/40 text-green-300'
              : 'border-yellow-800 bg-yellow-950/40 text-yellow-300'
          }`}>
            {stripeRevenueRescueStatus} · {stripeRescueSummary.revenue_rescue_ready ? 'ready' : 'blocked'} · {formatDateTime(stripeRescue.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Checkout-ready offers', stripeRescueSummary.checkout_ready_offers],
            ['Offers checked', stripeRescueSummary.offers_checked],
            ['Tracked events', stripeRescueSummary.tracked_events],
            ['Checkout completed', stripeRescueSummary.checkout_completed],
            ['Payments won', stripeRescueSummary.payment_succeeded],
            ['Paid invoices', stripeRescueSummary.invoice_paid],
            ['Email recipients', stripeRescueSummary.payment_email_recipients],
            ['Email notices', stripeRescueSummary.payment_email_notices],
            ['GitHub alerts', stripeRescueSummary.github_payment_notifications_enabled ? 'On' : 'Off'],
            ['GitHub issues', stripeRescueSummary.github_payment_issues_created],
            ['Gross revenue', `$${((stripeRescueSummary.gross_revenue_cents ?? 0) / 100).toFixed(2)}`],
            ['Blockers', stripeRescueSummary.blocker_count],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{typeof value === 'number' ? formatNumber(value) : value}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_1fr]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Revenue blockers</h4>
            <div className="mt-3 space-y-2">
              {(stripeRescue.revenue_blockers ?? []).slice(0, 6).map((blocker) => (
                <div key={blocker} className="border-l-2 border-yellow-500 pl-3 text-xs leading-5 text-yellow-100">
                  {blocker}
                </div>
              ))}
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Next fixes</h4>
            <div className="mt-3 space-y-2">
              {(stripeRescue.priority_fixes ?? []).slice(0, 6).map((fix, index) => (
                <div key={fix} className="grid grid-cols-[1.5rem_1fr] gap-2 text-xs leading-5 text-slate-300">
                  <span className="font-mono text-dreamco-accent">{index + 1}</span>
                  <span>{fix}</span>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-500">{stripeRescue.safety_note}</p>
          </aside>
        </div>
      </section>

      <section aria-labelledby="storage-guard-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Memory storage guard</p>
            <h3 id="storage-guard-heading" className="mt-1 text-lg font-semibold text-white">💾 Future-proof bot memory</h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Enforces local-first storage budgets, generated library sharding, memory rollover, compaction, and manifest-first loading.
            </p>
          </div>
          <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
            storageSummary.storage_ready
              ? 'border-green-800 bg-green-950/40 text-green-300'
              : 'border-yellow-800 bg-yellow-950/40 text-yellow-300'
          }`}>
            {storageGuardStatus} · {storageSummary.storage_ready ? 'ready' : 'needs attention'} · {formatDateTime(storage.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Checks', storageSummary.checks],
            ['Failed', storageSummary.failed_checks],
            ['Warnings', storageSummary.warnings],
            ['Memory tiers', storageSummary.memory_tiers],
            ['Useful keep', storageSummary.useful_keep_categories],
            ['Useful drop', storageSummary.useful_drop_categories],
            ['Metadata rules', storageSummary.useful_required_metadata],
            ['Resource shards', storageSummary.resource_shard_count],
            ['Bot entries', storageSummary.bot_resource_entries_checked],
            ['Largest shard MB', storageSummary.largest_resource_shard_mb],
            ['Shard cap MB', storage.budgets?.generated_resource_shard_max_mb],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Rollover tiers</h4>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {(storage.memory_tiers ?? []).map((tier) => (
                <div key={tier.tier} className="border border-slate-800 bg-slate-950 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-white">{formatLabel(tier.tier)}</p>
                    <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[11px] text-slate-300">
                      {tier.rollover_at_mb} MB
                    </span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{tier.purpose}</p>
                </div>
              ))}
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Never one giant memory file</h4>
            <div className="mt-3 space-y-2">
              {(storage.partitioning_rules ?? []).slice(0, 5).map((rule) => (
                <div key={rule} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                  {rule}
                </div>
              ))}
            </div>
            {(storage.warnings ?? []).length > 0 && (
              <div className="mt-4 border border-yellow-800 bg-yellow-950/20 p-3 text-xs leading-5 text-yellow-200">
                {(storage.warnings ?? []).join(' · ')}
              </div>
            )}
          </aside>
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_22rem]">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Only useful data gets stored</h4>
            <p className="mt-2 text-xs leading-5 text-slate-400">{storage.useful_data_policy?.rule}</p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div className="border border-slate-800 bg-slate-950 p-3">
                <h5 className="text-xs font-semibold uppercase text-green-300">Keep</h5>
                <div className="mt-3 space-y-2">
                  {(storage.useful_data_policy?.keep_categories ?? []).slice(0, 6).map((item) => (
                    <p key={item} className="text-xs leading-5 text-slate-300">{formatLabel(item)}</p>
                  ))}
                </div>
              </div>
              <div className="border border-slate-800 bg-slate-950 p-3">
                <h5 className="text-xs font-semibold uppercase text-yellow-300">Drop</h5>
                <div className="mt-3 space-y-2">
                  {(storage.useful_data_policy?.drop_categories ?? []).slice(0, 6).map((item) => (
                    <p key={item} className="text-xs leading-5 text-slate-300">{formatLabel(item)}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Required usefulness metadata</h4>
            <div className="mt-3 space-y-2">
              {(storage.useful_data_policy?.required_metadata ?? []).slice(0, 8).map((field) => (
                <div key={field} className="border-l-2 border-dreamco-accent pl-3 text-xs leading-5 text-slate-300">
                  {formatLabel(field)}
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              Minimum score to store: {storage.useful_data_policy?.minimum_usefulness_score_to_store ?? 3}
            </p>
          </aside>
        </div>
      </section>

      <section aria-labelledby="github-triage-heading" className="border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Repository retest scan</p>
            <h3 id="github-triage-heading" className="mt-1 text-lg font-semibold text-white">🔎 GitHub PR, issue, and comment triage</h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Scans pull requests, issues, conversation comments, review comments, workflow runs, and the PR restart queue.
            </p>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-400">
            {githubTriageStatus} · {formatDateTime(triage.generated_at)}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden border border-slate-800 bg-slate-800 lg:grid-cols-4 xl:grid-cols-8">
          {[
            ['Open PRs', triageSummary.open_prs],
            ['Open issues', triageSummary.open_issues],
            ['Issue comments', triageSummary.issue_comments_scanned],
            ['Review comments', triageSummary.pr_review_comments_scanned],
            ['Workflow runs', triageSummary.workflow_runs_scanned],
            ['Failed runs', triageSummary.failed_workflow_runs],
            ['Active runs', triageSummary.active_workflow_runs],
            ['Restart queue', triageSummary.pr_restart_queue],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-900 p-4">
              <p className="text-xl font-black text-white">{formatNumber(value)}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-white">Buddy help for every pull request</h4>
              <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-400">
                Every pull request should get Buddy help: scan, explain, retest, repair, and package before owner review.
              </p>
            </div>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-300">
              {formatNumber(triageSummary.open_prs)} open PRs watched
            </span>
          </div>
          <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-5">
            {PR_BUDDY_HELP_FLOW.map(([title, detail], index) => (
              <div key={title} className="min-h-32 bg-slate-950 p-3">
                <p className="font-mono text-[11px] text-dreamco-accent">0{index + 1}</p>
                <h5 className="mt-2 text-sm font-semibold text-white">{title}</h5>
                <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-5 border border-yellow-800 bg-yellow-950/10 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-white">Failed pull request rescue</h4>
              <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-300">
                When a pull request fails checks or gets blocked by comments, Buddy turns it into a fix packet:
                blocker, cause, patch plan, retest proof, and review-ready summary.
              </p>
            </div>
            <span className="rounded-full border border-yellow-700 px-3 py-1 text-xs font-semibold text-yellow-200">
              {formatNumber((triage.pr_restart_queue ?? []).length + (triage.failed_workflow_runs ?? []).length)} rescue signal(s)
            </span>
          </div>

          <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-5">
            {FAILED_PR_RESCUE_FLOW.map(([title, detail], index) => (
              <div key={title} className="min-h-32 bg-slate-950 p-3">
                <p className="font-mono text-[11px] text-yellow-300">0{index + 1}</p>
                <h5 className="mt-2 text-sm font-semibold text-white">{title}</h5>
                <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(0,1fr)_20rem]">
            <div className="border border-slate-800 bg-slate-950 p-3">
              <h5 className="text-xs font-semibold uppercase text-slate-300">Active failed PR help queue</h5>
              <div className="mt-3 space-y-2">
                {(triage.pr_restart_queue ?? []).slice(0, 4).map((pr) => (
                  <a key={`failed-pr-${pr.number}`} href={pr.url} className="block border-l-2 border-yellow-500 pl-3 text-xs leading-5 text-slate-300 hover:text-white">
                    <span className="font-semibold text-white">#{pr.number}</span> {pr.title}
                    <span className="block text-slate-500">
                      Buddy rescue: rebase or retest, inspect comments, repair failing gates, then package review notes.
                    </span>
                  </a>
                ))}
                {(triage.pr_restart_queue ?? []).length === 0 && (
                  <p className="text-xs leading-5 text-green-300">No failed or stale PRs need Buddy rescue in the latest scan.</p>
                )}
              </div>
            </div>

            <aside className="border border-slate-800 bg-slate-950 p-3">
              <h5 className="text-xs font-semibold uppercase text-slate-300">Owner gates</h5>
              <div className="mt-3 space-y-2">
                {FAILED_PR_OWNER_GATES.map((gate) => (
                  <p key={gate} className="text-xs leading-5 text-slate-400">{gate}</p>
                ))}
              </div>
            </aside>
          </div>
        </div>

        <div className="mt-5 border border-slate-800 bg-slate-900 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-white">Past failure rebuild backlog</h4>
              <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-400">
                Buddy turns scanned historical PR failures, workflow runs, quality gates, agent failures, and integration blockers
                into rebuild packets so old breakage gets rebuilt, retested, or assigned instead of forgotten.
              </p>
            </div>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-300">
              {formatNumber(pastFailureRebuildPackets.length)} rebuild packet(s)
            </span>
          </div>

          <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-5">
            {PAST_FAILURE_REBUILD_FLOW.map(([title, detail], index) => (
              <div key={title} className="min-h-32 bg-slate-950 p-3">
                <p className="font-mono text-[11px] text-dreamco-accent">0{index + 1}</p>
                <h5 className="mt-2 text-sm font-semibold text-white">{title}</h5>
                <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 grid gap-3 xl:grid-cols-[minmax(0,1fr)_22rem]">
            <div className="grid gap-3 md:grid-cols-2">
              {pastFailureRebuildPackets.slice(0, 8).map((packet) => (
                <article key={packet.id} className="border border-slate-800 bg-slate-950 p-3">
                  <p className="text-[11px] font-bold uppercase text-dreamco-accent">{packet.source}</p>
                  <h5 className="mt-1 text-sm font-semibold text-white">{packet.title}</h5>
                  <p className="mt-1 break-words font-mono text-[11px] text-slate-500">{packet.target}</p>
                  <p className="mt-3 text-xs leading-5 text-slate-300">{packet.build}</p>
                  <p className="mt-2 text-xs leading-5 text-yellow-100">{packet.proof}</p>
                </article>
              ))}
              {pastFailureRebuildPackets.length === 0 && (
                <p className="border border-green-800 bg-green-950/20 p-3 text-sm text-green-300">
                  No past failure rebuild packets found in the latest scan.
                </p>
              )}
            </div>

            <aside className="border border-slate-800 bg-slate-950 p-3">
              <h5 className="text-xs font-semibold uppercase text-slate-300">Rebuild rules</h5>
              <div className="mt-3 space-y-2">
                {PAST_FAILURE_REBUILD_GATES.map((gate) => (
                  <p key={gate} className="text-xs leading-5 text-slate-400">{gate}</p>
                ))}
              </div>
            </aside>
          </div>
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">PR restart and retest queue</h4>
            <div className="mt-3 space-y-2">
              {(triage.pr_restart_queue ?? []).slice(0, 6).map((pr) => (
                <a
                  key={pr.number}
                  href={pr.url}
                  className="block border-l-2 border-dreamco-accent pl-3 text-sm text-slate-300 hover:text-white"
                >
                  <span className="font-semibold text-white">#{pr.number}</span> {pr.title}
                  <span className="block text-xs text-slate-500">
                    {pr.head_branch} · {formatNumber(pr.age_days)} days · {(pr.restart_reasons ?? []).map(formatLabel).join(', ')}
                  </span>
                </a>
              ))}
              {(triage.pr_restart_queue ?? []).length === 0 && (
                <p className="text-sm text-green-300">No restart queue items found in the latest scan.</p>
              )}
            </div>
          </div>

          <div className="border border-slate-800 bg-slate-900 p-4">
            <h4 className="text-sm font-semibold text-white">Workflow failures to retest</h4>
            <div className="mt-3 space-y-2">
              {(triage.failed_workflow_runs ?? []).slice(0, 6).map((run) => (
                <a
                  key={run.id}
                  href={run.url}
                  className="block border-l-2 border-yellow-500 pl-3 text-sm text-slate-300 hover:text-white"
                >
                  <span className="font-semibold text-white">{run.name}</span>
                  <span className="block text-xs text-slate-500">
                    {run.branch} · {formatLabel(run.conclusion)} · {formatDateTime(run.updated_at)}
                  </span>
                </a>
              ))}
              {(triage.failed_workflow_runs ?? []).length === 0 && (
                <p className="text-sm text-green-300">No failed workflow runs in the scanned window.</p>
              )}
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              Workflow reruns require authenticated GitHub Actions permission; this page keeps the retest queue visible.
            </p>
          </div>
        </div>
      </section>

      <section aria-labelledby="builders-heading">
        <div className="mb-4 flex items-end justify-between gap-3">
          <div>
            <h3 id="builders-heading" className="text-lg font-semibold text-white">Builder lanes</h3>
            <p className="mt-1 text-sm text-slate-400">Choose the system boundary; every lane emits tests and documentation.</p>
          </div>
          <span className="text-xs text-slate-500">Source: {libraryStatus}</span>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-2" role="tablist" aria-label="System builders">
          {builders.map((builder) => (
            <button
              key={builder.id}
              type="button"
              role="tab"
              aria-selected={selectedBuilder.id === builder.id}
              onClick={() => {
                setSelectedBuilderId(builder.id);
                setBuildPacket(null);
              }}
              className={`min-w-40 rounded-md border px-3 py-3 text-left text-sm font-semibold ${
                selectedBuilder.id === builder.id
                  ? 'border-dreamco-accent bg-dreamco-accent/15 text-white'
                  : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500'
              }`}
            >
              <span className="mr-2 text-lg" aria-hidden="true">{builder.icon}</span>
              {builder.name}
            </button>
          ))}
        </div>

        <div className="mt-4 grid gap-5 border border-slate-700 bg-slate-950 p-5 xl:grid-cols-[minmax(0,1fr)_18rem]">
          <div>
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase text-slate-500">Selected builder</p>
                <h4 className="mt-1 text-xl font-bold text-white">{selectedBuilder.icon} {selectedBuilder.name}</h4>
              </div>
              <button
                type="button"
                onClick={prepareBuildPacket}
                className="rounded-md bg-dreamco-accent px-4 py-2 text-sm font-semibold text-white hover:bg-dreamco-accent/80"
              >
                Prepare build packet
              </button>
            </div>
            <div className="grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-3">
              {BUILD_STAGES.map(([number, title, detail]) => (
                <div key={number} className="min-h-32 bg-slate-900 p-4">
                  <span className="font-mono text-xs text-dreamco-accent">{number}</span>
                  <h5 className="mt-2 font-semibold text-white">{title}</h5>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{detail}</p>
                </div>
              ))}
            </div>
          </div>
          <aside className="border-l border-slate-800 pl-5">
            <h5 className="text-sm font-semibold text-white">Build outputs</h5>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              {selectedBuilder.outputs.map((output) => (
                <li key={output}>✓ {formatLabel(output)}</li>
              ))}
            </ul>
            <p className="mt-5 text-xs leading-5 text-yellow-300">
              Review gate: {formatLabel(selectedBuilder.approval)}
            </p>
          </aside>
        </div>

        {buildPacket && (
          <div role="status" className="mt-3 border border-green-800 bg-green-950/30 p-4 text-sm text-green-300">
            Build packet prepared for {buildPacket.builder}. It is sandbox-only until a reviewed pull request approves deployment.
          </div>
        )}
      </section>

      <section aria-labelledby="libraries-heading">
        <h3 id="libraries-heading" className="text-lg font-semibold text-white">Generated libraries</h3>
        <p className="mt-1 text-sm text-slate-400">Every library contains one governed contract for every registered bot.</p>
        <div className="mt-4 grid gap-5 lg:grid-cols-[15rem_minmax(0,1fr)]">
          <div className="border border-slate-700 bg-slate-950 p-2" role="tablist" aria-label="Generated libraries">
            {libraries.map((library) => (
              <button
                key={library.id}
                type="button"
                role="tab"
                aria-selected={activeLibrary === library.id}
                onClick={() => setActiveLibrary(library.id)}
                className={`flex w-full items-center justify-between px-3 py-2 text-left text-sm ${
                  activeLibrary === library.id
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <span>{library.icon} {library.name}</span>
                <span className="font-mono text-xs">{library.count}</span>
              </button>
            ))}
          </div>
          <div className="border border-slate-700 bg-slate-900 p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-3xl" aria-hidden="true">{selectedLibrary.icon}</p>
                <h4 className="mt-2 text-xl font-bold text-white">{selectedLibrary.name}</h4>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">{selectedLibrary.description}</p>
              </div>
              <span className="rounded-full border border-green-800 bg-green-950/30 px-3 py-1 text-xs font-semibold text-green-300">
                {selectedLibrary.count} / {botCount} covered
              </span>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="border border-slate-700 p-3"><p className="text-xs text-slate-500">Schema</p><p className="mt-1 text-sm text-white">Versioned JSON</p></div>
              <div className="border border-slate-700 p-3"><p className="text-xs text-slate-500">Validation</p><p className="mt-1 text-sm text-white">Generator drift check</p></div>
              <div className="border border-slate-700 p-3"><p className="text-xs text-slate-500">Delivery</p><p className="mt-1 text-sm text-white">Pull request</p></div>
            </div>

            <div className="mt-5 border border-emerald-800 bg-emerald-950/20 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase text-emerald-200">Sandbox bootcamp generator</p>
                  <h5 className="mt-1 text-sm font-semibold text-white">{bootcampBaseline.name}</h5>
                  <p className="mt-1 max-w-2xl text-xs leading-5 text-emerald-100/80">
                    Every API sandbox test now has a workflow generator, and every sandbox is packaged as a bot-building bootcamp
                    for you, Buddy, and clients.
                  </p>
                </div>
                <span className="rounded-full border border-emerald-500/40 px-3 py-1 text-xs font-semibold text-emerald-200">
                  {formatNumber(bootcampBaseline.top_ai_company_resource_seed_count)} AI practice seeds
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-px overflow-hidden border border-emerald-900 bg-emerald-900 md:grid-cols-4">
                {[
                  ['Custom APIs', libraryCoverage.bots_with_custom_api_contracts],
                  ['API bootcamps', libraryCoverage.bots_with_api_sandbox_bootcamps],
                  ['Workflow generators', libraryCoverage.bots_with_sandbox_workflow_generators],
                  ['Training tracks', libraryCoverage.bots_with_owner_buddy_client_bootcamp_tracks],
                  ['Resource seeds', libraryCoverage.bots_with_top_ai_company_resource_seeds],
                ].map(([label, value]) => (
                  <div key={label} className="bg-slate-950 p-3">
                    <p className="text-lg font-black text-white">{formatNumber(value ?? botCount)}</p>
                    <p className="mt-1 text-xs uppercase text-emerald-100/70">{label}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 grid gap-4 lg:grid-cols-3">
                <div className="border border-slate-800 bg-slate-950 p-3">
                  <p className="text-xs font-semibold uppercase text-slate-400">Audiences</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(bootcampBaseline.audiences ?? []).map((audience) => (
                      <span key={audience} className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
                        {formatLabel(audience)}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="border border-slate-800 bg-slate-950 p-3">
                  <p className="text-xs font-semibold uppercase text-slate-400">World-class sandbox rules</p>
                  <p className="mt-2 text-xs leading-5 text-slate-300">
                    {(bootcampBaseline.sandbox_principles ?? []).slice(0, 4).map(formatLabel).join(' · ')}
                  </p>
                </div>
                <div className="border border-slate-800 bg-slate-950 p-3">
                  <p className="text-xs font-semibold uppercase text-slate-400">Source boundaries</p>
                  <p className="mt-2 text-xs leading-5 text-slate-300">
                    {(bootcampBaseline.source_boundaries ?? []).slice(0, 3).map(formatLabel).join(' · ')}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <div className="border border-slate-700 bg-slate-950 p-5">
          <h3 className="text-lg font-semibold text-white">GitHub engineering signals</h3>
          <div className="mt-4 divide-y divide-slate-800">
            {GITHUB_SIGNALS.map((signal) => (
              <div key={signal.title} className="py-3">
                <h4 className="text-sm font-semibold text-white">{signal.title}</h4>
                <p className="mt-1 text-xs leading-5 text-slate-400">{signal.detail}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="border border-slate-700 bg-slate-950 p-5">
          <h3 className="text-lg font-semibold text-white">Sandbox release gates</h3>
          <div className="mt-4 space-y-3">
            {SAFETY_GATES.map((gate) => (
              <label key={gate} className="flex items-start gap-3 text-sm text-slate-300">
                <input type="checkbox" checked readOnly className="mt-0.5 h-4 w-4 accent-green-500" />
                <span>{gate}</span>
              </label>
            ))}
          </div>
        </div>
      </section>

      <ActionsMonitorComponent />

      {showBuddyCenter && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/85 px-4 py-6"
          onClick={() => setShowBuddyCenter(false)}
        >
          <div onClick={(event) => event.stopPropagation()}>
            <BuddyCommandCenter
              onClose={() => setShowBuddyCenter(false)}
              onCommandSubmit={submitBuddyPrompt}
            />
          </div>
        </div>
      )}
    </section>
  );
}
