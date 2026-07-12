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
  checks: [{ name: 'resource_sharding_integrity', status: 'pass', message: 'resources are sharded and count-safe' }],
  warnings: [],
};

function StubActionsMonitor() {
  return <div>Actions monitor panel</div>;
}

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    let payload = libraryPayload;
    if (url === '/api/buddy-capabilities') payload = buddyCapabilityPayload;
    if (url === '/api/github-triage') payload = githubTriagePayload;
    if (url === '/api/repository-stewardship') payload = repositoryStewardshipPayload;
    if (url === '/api/buddy-productivity') payload = buddyProductivityPayload;
    if (url === '/api/storage-guard') payload = storageGuardPayload;
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
    expect(screen.getByRole('heading', { name: 'Professional delivery pipeline' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Client vibe building for apps, videos, courses, games, and simulations' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'AI company builder with human trust built in' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Tracks what helps you, clients, and bots improve' })).toBeInTheDocument();
    expect(screen.getByText('AI companies')).toBeInTheDocument();
    expect(screen.getByText('Human trust')).toBeInTheDocument();
    expect(screen.getByText('Music video')).toBeInTheDocument();
    expect(screen.getByText('Kids learning video')).toBeInTheDocument();
    expect(screen.getByText('College course')).toBeInTheDocument();
    expect(screen.getByText('Video game')).toBeInTheDocument();
    expect(screen.getByText('Simulation')).toBeInTheDocument();
    expect(screen.getByText('Voice and image consent rules')).toBeInTheDocument();
    expect(screen.getByText(/No fake testimonials/)).toBeInTheDocument();
    expect(screen.getByText('Builder lanes')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '🤝 Buddy capability tracker' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '🧪 Buddy and bot test catalog' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Always-clean PR, issue, and code-quality steward' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '💾 Future-proof bot memory' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '🔎 GitHub PR, issue, and comment triage' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Generated libraries' })).toBeInTheDocument();
    expect(screen.getByText('Actions monitor panel')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Source: live')).toBeInTheDocument());
    expect(screen.getAllByText('1,248').length).toBeGreaterThan(0);
    expect(screen.getByText('8,736')).toBeInTheDocument();
  });

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
    expect(screen.getByText('All bots have a path')).toBeInTheDocument();
    expect(screen.getByText('Review placeholders')).toBeInTheDocument();
    expect(screen.getByText('Add direct tests')).toBeInTheDocument();
    expect(screen.getByText('Production readiness')).toBeInTheDocument();
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

    await waitFor(() => expect(screen.getByText('Buddy Bot')).toBeInTheDocument());
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
    expect(screen.getByText('PR restart and retest queue')).toBeInTheDocument();
    expect(screen.getByText(/Finish Buddy readiness tracker/)).toBeInTheDocument();
    expect(screen.getByText('Workflow failures to retest')).toBeInTheDocument();
    expect(screen.getByText('Rollover tiers')).toBeInTheDocument();
    expect(screen.getByText('Never one giant memory file')).toBeInTheDocument();
    expect(screen.getByText('System and Bot Builds Monitoring')).toBeInTheDocument();
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

  it('opens and closes the Buddy build console', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    fireEvent.click(screen.getByRole('button', { name: 'Open Buddy Live Console' }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Close Buddy Command Center' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
