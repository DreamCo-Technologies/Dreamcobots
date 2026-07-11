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
];

const FALLBACK_LIBRARIES = [
  { id: 'tools', name: 'Tools Library', icon: '🔧', count: 1247, description: 'Typed, permission-aware tools with tests and audit metadata.' },
  { id: 'apis', name: 'Apis Library', icon: '🔌', count: 1247, description: 'Versioned per-bot APIs with schemas, rate limits, and approval gates.' },
  { id: 'webhooks', name: 'Webhooks Library', icon: '🪝', count: 1247, description: 'Signed, idempotent per-bot event contracts with queued processing.' },
  { id: 'workflows', name: 'Workflows Library', icon: '🔁', count: 1247, description: 'Reusable validation and delivery workflows with least privilege.' },
  { id: 'skills', name: 'Skills Library', icon: '🧠', count: 1247, description: 'Versioned multi-step skills with evidence and tests.' },
  { id: 'sandboxes', name: 'Sandboxes Library', icon: '🧪', count: 1247, description: 'Isolated test environments with fixtures, limits, and no live money movement.' },
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
    { slug: 'buddy_core', name: 'Buddy Core', build_state: 'built_and_test_covered', test_state: 'ready_for_test_run' },
    { slug: 'buddy_orchestrator', name: 'Buddy Orchestrator', build_state: 'built_and_test_covered', test_state: 'ready_for_test_run' },
    { slug: 'buddy-tool-builder', name: 'Buddy Tool Library Builder Bot', build_state: 'built_contract_ready', test_state: 'ready_for_contract_testing' },
  ],
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

export default function ActionsPage({
  ActionsMonitorComponent = ActionsMonitor,
  onBuddyCommandSubmit = () => {},
  onBuildRequest = () => {},
}) {
  const [showBuddyCenter, setShowBuddyCenter] = useState(false);
  const [selectedBuilderId, setSelectedBuilderId] = useState('full-bot-system');
  const [activeLibrary, setActiveLibrary] = useState('tools');
  const [libraryData, setLibraryData] = useState(null);
  const [libraryStatus, setLibraryStatus] = useState('loading');
  const [buddyInventory, setBuddyInventory] = useState(null);
  const [buddyInventoryStatus, setBuddyInventoryStatus] = useState('loading');
  const [githubTriage, setGithubTriage] = useState(null);
  const [githubTriageStatus, setGithubTriageStatus] = useState('loading');
  const [buildPacket, setBuildPacket] = useState(null);

  useEffect(() => {
    fetch('/api/system-libraries')
      .then((response) => {
        if (!response.ok) throw new Error(`Library API returned ${response.status}`);
        return response.json();
      })
      .then((data) => {
        setLibraryData(data);
        setLibraryStatus('live');
      })
      .catch(() => setLibraryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetch('/api/buddy-capabilities')
      .then((response) => {
        if (!response.ok) throw new Error(`Buddy capability API returned ${response.status}`);
        return response.json();
      })
      .then((data) => {
        setBuddyInventory(data);
        setBuddyInventoryStatus('live');
      })
      .catch(() => setBuddyInventoryStatus('generated fallback'));
  }, []);

  useEffect(() => {
    fetch('/api/github-triage')
      .then((response) => {
        if (!response.ok) throw new Error(`GitHub triage API returned ${response.status}`);
        return response.json();
      })
      .then((data) => {
        setGithubTriage(data);
        setGithubTriageStatus('live');
      })
      .catch(() => setGithubTriageStatus('generated fallback'));
  }, []);

  const builders = libraryData?.builders ?? FALLBACK_BUILDERS;
  const libraries = libraryData?.libraries ?? FALLBACK_LIBRARIES;
  const botCount = libraryData?.bot_count ?? 1247;
  const inventory = buddyInventory ?? FALLBACK_BUDDY_INVENTORY;
  const triage = githubTriage ?? FALLBACK_GITHUB_TRIAGE;
  const inventorySummary = inventory.summary ?? FALLBACK_BUDDY_INVENTORY.summary;
  const triageSummary = triage.summary ?? FALLBACK_GITHUB_TRIAGE.summary;
  const buildStates = inventorySummary.build_states ?? {};
  const testStates = inventorySummary.test_states ?? {};
  const codingPathStates = inventorySummary.coding_path_states ?? {};
  const productionStates = inventorySummary.production_readiness_states ?? {};
  const needsImplementation = inventory.attention?.needs_implementation ?? [];
  const needsDirectTests = inventory.attention?.needs_direct_test_coverage ?? [];
  const needsSystemMapping = inventory.attention?.needs_existing_system_mapping ?? [];
  const directBuddyBots = inventory.buddy_bots ?? [];
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

  return (
    <section className="space-y-6">
      <header className="border-b border-slate-700 pb-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">DreamCo Build Operations</p>
            <h2 className="mt-1 text-2xl font-bold text-white">🛠️ System Builder Hub</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Build complete bots and their tools, APIs, webhooks, workflows, skills,
              and isolated test environments from governed contracts.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowBuddyCenter(true)}
            className="rounded-md bg-dreamco-accent px-4 py-2 text-sm font-semibold text-white hover:bg-dreamco-accent/80"
          >
            Open Buddy Build Console
          </button>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden rounded-md border border-slate-700 bg-slate-700 lg:grid-cols-4">
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
                  {inventorySummary.all_bots_production_ready ? 'All bots production-ready' : 'Production blockers remain'}
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
