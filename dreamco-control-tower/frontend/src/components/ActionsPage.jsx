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

function formatLabel(value) {
  return String(value || '').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
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
  const [storageGuard, setStorageGuard] = useState(null);
  const [storageGuardStatus, setStorageGuardStatus] = useState('loading');
  const [buildPacket, setBuildPacket] = useState(null);

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
    fetchFirstJson(['/api/storage-guard'])
      .then((data) => {
        setStorageGuard(data);
        setStorageGuardStatus('live');
      })
      .catch(() => setStorageGuardStatus('generated fallback'));
  }, []);

  const builders = libraryData?.builders ?? FALLBACK_BUILDERS;
  const libraries = libraryData?.libraries ?? FALLBACK_LIBRARIES;
  const botCount = libraryData?.bot_count ?? 1247;
  const inventory = buddyInventory ?? FALLBACK_BUDDY_INVENTORY;
  const triage = githubTriage ?? FALLBACK_GITHUB_TRIAGE;
  const stewardship = repositoryStewardship ?? FALLBACK_REPOSITORY_STEWARDSHIP;
  const productivity = buddyProductivity ?? FALLBACK_BUDDY_PRODUCTIVITY;
  const storage = storageGuard ?? FALLBACK_STORAGE_GUARD;
  const inventorySummary = inventory.summary ?? FALLBACK_BUDDY_INVENTORY.summary;
  const triageSummary = triage.summary ?? FALLBACK_GITHUB_TRIAGE.summary;
  const stewardshipSummary = stewardship.summary ?? FALLBACK_REPOSITORY_STEWARDSHIP.summary;
  const productivitySummary = productivity.summary ?? FALLBACK_BUDDY_PRODUCTIVITY.summary;
  const storageSummary = storage.summary ?? FALLBACK_STORAGE_GUARD.summary;
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

  function prepareBotTest(bot, scope = 'selected') {
    const packet = buildBotTestPacket(bot, scope);
    setSelectedBotSlug(bot.slug);
    setBotTestPacket(packet);
    onBotTestRequest(packet);
  }

  return (
    <section className="space-y-6">
      <header className="overflow-hidden border border-slate-700 bg-slate-950">
        <div className="grid gap-6 p-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-xs font-bold uppercase text-dreamco-accent">Client Operations Preview</p>
              <span className="rounded-full border border-green-800 bg-green-950/40 px-3 py-1 text-xs font-semibold text-green-300">
                Live dashboard
              </span>
              <span className="rounded-full border border-yellow-800 bg-yellow-950/30 px-3 py-1 text-xs font-semibold text-yellow-300">
                Supervised autonomy
              </span>
            </div>
            <h2 className="mt-3 max-w-4xl text-3xl font-black tracking-normal text-white md:text-4xl">
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
                className="rounded-md bg-dreamco-accent px-4 py-2 text-sm font-semibold text-white hover:bg-dreamco-accent/80"
              >
                Open Buddy Live Console
              </button>
              <button
                type="button"
                onClick={() => prepareBotTest(botCatalog.find((bot) => bot.slug === 'buddy-bot') ?? selectedBot, 'buddy')}
                className="rounded-md border border-slate-600 px-4 py-2 text-sm font-semibold text-slate-200 hover:border-slate-400"
              >
                Prepare Buddy Test
              </button>
            </div>
          </div>
          <aside className="border border-slate-800 bg-slate-900 p-4">
            <h3 className="text-sm font-semibold text-white">Operational status</h3>
            <div className="mt-3 space-y-3">
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

        <div className="grid grid-cols-2 gap-px border-t border-slate-800 bg-slate-800 lg:grid-cols-4">
          {[
            ['Registered bots', botCount.toLocaleString()],
            ['Per-bot contracts', contractCount.toLocaleString()],
            ['System builders', builders.length],
            ['Generated libraries', libraries.length],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-950 p-4">
              <p className="text-2xl font-black text-white">{value}</p>
              <p className="mt-1 text-xs uppercase text-slate-500">{label}</p>
            </div>
          ))}
        </div>
      </header>

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
              onCommandSubmit={onBuddyCommandSubmit}
            />
          </div>
        </div>
      )}
    </section>
  );
}
