import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  MODEL_BENCHMARK_TARGETS,
  MODEL_DISCOVERY_TASKS,
} from "../shared/model-benchmark-targets";

type ModelTarget = (typeof MODEL_BENCHMARK_TARGETS)[number];
type CostMode = "free" | "premium";

type ProgressConfig = {
  schema: string;
  version: string;
  reviewed_on: string;
  mission: string;
  council_policy: {
    seats_per_task: number;
    task_categories: number;
    modes: CostMode[];
    free_eligible_tiers: string[];
    premium_eligible_tiers: string[];
    [key: string]: unknown;
  };
  readiness_gates: Array<{ id: string; label: string; description: string }>;
  benchmark_estimates: Record<string, { baseline_setup: string; first_gap_cycle: string }>;
  bootcamp_path: string[];
  continuous_improvement_policy: Record<string, unknown>;
  workstreams: Array<Record<string, unknown>>;
  dataset_package_policy: Record<string, unknown> & {
    template_count: number;
    records_included: number;
    allowed_inputs: string[];
    blocked_inputs: string[];
    required_artifacts: string[];
  };
  truth_contract: Record<string, boolean>;
};

type BenchmarkCatalog = {
  summary: Record<string, number>;
  suites: Array<{
    id: string;
    label: string;
    modality: string;
    grader: string;
    prompt_fixture: string;
    expected: string;
  }>;
  targets: Array<{
    id: number;
    benchmarkSuites: string[];
    catalogReady: boolean;
    sourceConnection: {
      sourceLinked: boolean;
      setupPathReady: boolean;
      setupPath: string[];
      connectorId: string | null;
      liveProviderConnection: boolean;
      liveProbePassed: boolean;
    };
    liveEvidenceStatus: string;
  }>;
};

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourcePath = resolve(root, "config", "buddy-model-progress-center.json");
const benchmarkPath = resolve(root, "config", "generated", "buddy_model_benchmarks.json");
const outputPath = resolve(root, "config", "generated", "buddy_model_progress_center.json");
const publicPath = resolve(root, "website", "data", "buddy-model-progress-center.js");

const config = JSON.parse(readFileSync(sourcePath, "utf8")) as ProgressConfig;
const benchmarkCatalog = JSON.parse(readFileSync(benchmarkPath, "utf8")) as BenchmarkCatalog;

const TASK_TERMS: Record<(typeof MODEL_DISCOVERY_TASKS)[number], string[]> = {
  "Coding": ["coding", "code", "developer", "software", "app", "debug", "repository"],
  "Reasoning": ["reasoning", "logic", "math", "analysis", "general chat", "decision"],
  "Research": ["research", "citation", "search", "evidence", "fact"],
  "Agents": ["agent", "autonomous", "workflow", "automation", "tool"],
  "Vision": ["vision", "image understanding", "visual", "ocr"],
  "Image Generation": ["image generation", "design", "art", "logo", "visual"],
  "Image Editing": ["image editing", "photo", "retouch", "inpaint", "design"],
  "Video": ["video", "film", "movie", "animation", "media"],
  "Voice and Speech": ["voice", "speech", "transcription", "narration", "audio"],
  "Music and Audio": ["music", "audio", "song", "sound", "voice"],
  "Multilingual and Translation": ["translation", "multilingual", "language", "writing"],
  "Safety and Moderation": ["safety", "moderation", "security", "compliance", "legal"],
  "OCR and Documents": ["ocr", "document", "pdf", "file", "legal"],
  "Search and Retrieval": ["search", "retrieval", "research", "embedding", "knowledge"],
  "Data Analysis": ["data", "analytics", "spreadsheet", "forecast", "finance"],
  "Embeddings": ["embedding", "vector", "retrieval", "semantic", "search"],
  "Forecasting": ["forecast", "prediction", "finance", "analytics", "trend"],
  "Simulation": ["simulation", "game", "education", "training", "agent"],
  "3D and Spatial": ["3d", "spatial", "world", "scene", "video", "image"],
  "Accessibility": ["accessibility", "caption", "voice", "education", "translation"],
};

const CATEGORY_TO_TASK: Record<string, (typeof MODEL_DISCOVERY_TASKS)[number]> = {
  "general chat": "Reasoning",
  "research": "Research",
  "coding": "Coding",
  "autonomous agents": "Agents",
  "image generation": "Image Generation",
  "video & audio": "Video",
  "voice & speech": "Voice and Speech",
  "writing & content": "Multilingual and Translation",
  "business & crm": "Agents",
  "no-code/low-code": "Coding",
  "customer support": "Agents",
  "data & analytics": "Data Analysis",
  "finance & trading": "Forecasting",
  "healthcare ai": "Research",
  "legal & compliance": "Safety and Moderation",
  "education": "Accessibility",
  "marketing & seo": "Search and Retrieval",
};

const TASK_SUITES: Record<(typeof MODEL_DISCOVERY_TASKS)[number], string[]> = {
  "Coding": ["instruction_following", "structured_output", "code_generation", "code_repair", "tool_selection", "safety_boundary"],
  "Reasoning": ["instruction_following", "structured_output", "arithmetic_reasoning", "long_context_retrieval", "safety_boundary"],
  "Research": ["instruction_following", "grounded_research", "long_context_retrieval", "safety_boundary"],
  "Agents": ["instruction_following", "structured_output", "tool_selection", "code_repair", "safety_boundary"],
  "Vision": ["instruction_following", "vision_understanding", "structured_output", "safety_boundary"],
  "Image Generation": ["instruction_following", "vision_understanding", "structured_output", "safety_boundary"],
  "Image Editing": ["instruction_following", "vision_understanding", "structured_output", "safety_boundary"],
  "Video": ["instruction_following", "vision_understanding", "audio_understanding", "safety_boundary"],
  "Voice and Speech": ["instruction_following", "audio_understanding", "multilingual", "safety_boundary"],
  "Music and Audio": ["instruction_following", "audio_understanding", "structured_output", "safety_boundary"],
  "Multilingual and Translation": ["instruction_following", "multilingual", "long_context_retrieval", "safety_boundary"],
  "Safety and Moderation": ["instruction_following", "structured_output", "safety_boundary", "grounded_research"],
  "OCR and Documents": ["instruction_following", "structured_output", "long_context_retrieval", "grounded_research", "safety_boundary"],
  "Search and Retrieval": ["instruction_following", "grounded_research", "long_context_retrieval", "tool_selection", "safety_boundary"],
  "Data Analysis": ["instruction_following", "structured_output", "arithmetic_reasoning", "tool_selection", "safety_boundary"],
  "Embeddings": ["instruction_following", "structured_output", "long_context_retrieval", "safety_boundary"],
  "Forecasting": ["instruction_following", "structured_output", "arithmetic_reasoning", "grounded_research", "safety_boundary"],
  "Simulation": ["instruction_following", "structured_output", "code_generation", "tool_selection", "safety_boundary"],
  "3D and Spatial": ["instruction_following", "vision_understanding", "structured_output", "code_generation", "safety_boundary"],
  "Accessibility": ["instruction_following", "multilingual", "vision_understanding", "audio_understanding", "safety_boundary"],
};

function normalize(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function slug(value: string) {
  return normalize(value).replace(/\s+/g, "-");
}

function primaryTask(target: ModelTarget) {
  if (MODEL_DISCOVERY_TASKS.includes(target.category as (typeof MODEL_DISCOVERY_TASKS)[number])) {
    return target.category as (typeof MODEL_DISCOVERY_TASKS)[number];
  }
  return CATEGORY_TO_TASK[normalize(target.category)] || "Reasoning";
}

function accessLane(tier: string) {
  if (tier === "free") return "free_available";
  if (tier === "freemium") return "free_limits_with_paid_upgrade";
  if (tier === "paid") return "paid_only";
  return "official_catalog_discovery";
}

function taskScore(target: ModelTarget, task: (typeof MODEL_DISCOVERY_TASKS)[number], mode: CostMode) {
  const searchable = normalize([target.name, target.provider, target.category, target.bestFor, ...target.declaredCapabilities].join(" "));
  const exactCategory = primaryTask(target) === task ? 120 : 0;
  const termMatches = TASK_TERMS[task].filter((term) => searchable.includes(normalize(term))).length;
  const tierScore = mode === "free"
    ? target.tier === "free" ? 18 : 10
    : target.tier === "paid" ? 18 : 12;
  const buddyLocal = target.provider === "DreamCo" ? 12 : 0;
  return exactCategory + termMatches * 13 + tierScore + buddyLocal;
}

function buildCouncil(task: (typeof MODEL_DISCOVERY_TASKS)[number], mode: CostMode) {
  const eligibleTiers = mode === "free"
    ? config.council_policy.free_eligible_tiers
    : config.council_policy.premium_eligible_tiers;
  const ranked = MODEL_BENCHMARK_TARGETS
    .filter((target) => !target.discoveryTarget && eligibleTiers.includes(target.tier))
    .map((target) => ({ target, score: taskScore(target, task, mode) }))
    .sort((left, right) => right.score - left.score || left.target.id - right.target.id);
  const chosen: typeof ranked = [];
  const providers = new Set<string>();
  for (const candidate of ranked) {
    const provider = normalize(candidate.target.provider);
    if (providers.has(provider)) continue;
    providers.add(provider);
    chosen.push(candidate);
    if (chosen.length === config.council_policy.seats_per_task) break;
  }
  for (const candidate of ranked) {
    if (chosen.length >= config.council_policy.seats_per_task) break;
    if (chosen.some((item) => item.target.id === candidate.target.id)) continue;
    chosen.push(candidate);
  }
  if (chosen.length !== config.council_policy.seats_per_task) {
    throw new Error(`Expected ${config.council_policy.seats_per_task} ${mode} council seats for ${task}, found ${chosen.length}`);
  }
  return {
    id: `${slug(task)}-${mode}`,
    task,
    mode,
    status: "provisional_metadata_council",
    selectionBasis: "Declared task fit, access tier, and provider diversity. No live quality score contributes yet.",
    liveBenchmarkContribution: 0,
    paidApprovalRequired: mode === "premium",
    members: chosen.map(({ target, score }, index) => ({
      rank: index + 1,
      targetId: target.id,
      name: target.name,
      provider: target.provider,
      category: target.category,
      tier: target.tier,
      accessLane: accessLane(target.tier),
      declaredBestFor: target.bestFor,
      metadataFitScore: score,
      metadataFitIsQualityScore: false,
      readiness: target.provider === "DreamCo" ? "local_route_ready" : "exact_model_and_adapter_evidence_required",
    })),
  };
}

function datasetPackages() {
  const packages = MODEL_DISCOVERY_TASKS.flatMap((task, index) => {
    const kinds = [
      { id: "synthetic-skill-drills", label: "Synthetic skill drills", use: "Practice instruction following and task completion on generated, non-personal examples." },
      { id: "held-out-evaluation", label: "Held-out evaluation", use: "Measure capability change on isolated examples that are never used for training." },
      ...(index < 10 ? [{ id: "adversarial-recovery", label: "Adversarial recovery", use: "Test malformed inputs, prompt injection, ambiguity, tool failure, and safe recovery." }] : []),
    ];
    return kinds.map((kind) => ({
      id: `${slug(task)}-${kind.id}`,
      name: `${task} ${kind.label} Pack`,
      taskCategory: task,
      packageType: kind.id,
      intendedUse: kind.use,
      status: "template_only",
      recordsIncluded: 0,
      sellableVerified: false,
      allowedInputs: config.dataset_package_policy.allowed_inputs,
      blockedInputs: config.dataset_package_policy.blocked_inputs,
      requiredArtifacts: config.dataset_package_policy.required_artifacts,
      benchmarkSuites: TASK_SUITES[task],
      sandboxTrack: "config/data-package-maximal-testing-program.json",
      trainingTrack: "config/universal-model-training-library-data-pack-program.json",
      nextGate: "Add rights-cleared records, run every applicable test family, and prove held-out usefulness before release or sale.",
    }));
  });
  if (packages.length !== config.dataset_package_policy.template_count) {
    throw new Error(`Expected ${config.dataset_package_policy.template_count} dataset packages, found ${packages.length}`);
  }
  return packages;
}

function buildCatalog() {
  const benchmarkByTarget = new Map(benchmarkCatalog.targets.map((target) => [target.id, target]));
  const connections = MODEL_BENCHMARK_TARGETS.map((target) => {
    const evidence = benchmarkByTarget.get(target.id);
    if (!evidence) throw new Error(`Missing benchmark record for target ${target.id}`);
    const categorized = Boolean(primaryTask(target));
    const checks = {
      cataloged: evidence.catalogReady,
      categorized,
      sourceLinked: evidence.sourceConnection.sourceLinked,
      setupPathReady: evidence.sourceConnection.setupPathReady,
      exactVersionVerified: Boolean(target.exactModelId),
      adapterSandboxPassed: evidence.sourceConnection.liveProbePassed,
      liveBenchmarkPassed: evidence.liveEvidenceStatus === "passed",
    };
    const passed = Object.values(checks).filter(Boolean).length;
    const gaps = Object.entries(checks).filter(([, complete]) => !complete).map(([id]) => id);
    return {
      targetId: target.id,
      name: target.name,
      provider: target.provider,
      declaredCategory: target.category,
      primaryTaskCategory: primaryTask(target),
      tier: target.tier,
      accessLane: accessLane(target.tier),
      discoveryTarget: target.discoveryTarget,
      officialCatalog: target.officialCatalog,
      connectorId: evidence.sourceConnection.connectorId,
      setupPath: evidence.sourceConnection.setupPath,
      benchmarkSuites: evidence.benchmarkSuites,
      checks,
      completedGates: passed,
      totalGates: Object.keys(checks).length,
      completionPercent: Math.round((passed / Object.keys(checks).length) * 100),
      gaps,
      liveProviderConnection: evidence.sourceConnection.liveProviderConnection,
      liveBenchmarkEvidence: evidence.liveEvidenceStatus === "passed",
      nextAction: gaps.includes("exactVersionVerified")
        ? "Verify the exact current model ID, version, access terms, region, and price from the official source."
        : gaps.includes("adapterSandboxPassed")
          ? "Implement and pass the governed provider adapter sandbox."
          : gaps.includes("liveBenchmarkPassed")
            ? "Run comparable signed fixtures and record current evidence."
            : "Keep the source and benchmark evidence current.",
    };
  });
  if (connections.length !== 500) throw new Error(`Expected 500 model connection records, found ${connections.length}`);
  if (connections.some((item) => !item.primaryTaskCategory || !item.officialCatalog || !item.setupPath.length)) {
    throw new Error("Every model target must have a category, official source, and setup path.");
  }

  const councils = MODEL_DISCOVERY_TASKS.flatMap((task) => config.council_policy.modes.map((mode) => buildCouncil(task, mode)));
  const packages = datasetPackages();
  const benchmarkRoadmaps = benchmarkCatalog.suites.map((suite) => {
    const estimate = config.benchmark_estimates[suite.grader];
    if (!estimate) throw new Error(`Missing estimate policy for benchmark grader ${suite.grader}`);
    return {
      id: suite.id,
      label: suite.label,
      modality: suite.modality,
      grader: suite.grader,
      status: "fixture_contract_ready_live_baseline_required",
      liveBaselineCount: 0,
      verifiedOpenSourceGap: null,
      verifiedFrontierGap: null,
      baselineSetupEstimate: estimate.baseline_setup,
      firstGapCycleEstimate: estimate.first_gap_cycle,
      benchmarkReachEstimate: "Not estimable until a comparable live baseline and target threshold exist.",
      path: [
        "freeze a versioned fixture and grader",
        "run the same fixture across exact model versions",
        "record quality, failure, latency, reliability, and cost evidence",
        "separate open-weight and frontier baselines",
        "assign the largest verified gap to Buddy Bootcamp",
        "retest held-out fixtures and regressions before promotion",
      ],
    };
  });
  const bootcampTracks = MODEL_DISCOVERY_TASKS.map((task) => ({
    id: `${slug(task)}-bootcamp`,
    task,
    status: "curriculum_mapped_runner_evidence_required",
    benchmarkSuites: TASK_SUITES[task],
    councilIds: [`${slug(task)}-free`, `${slug(task)}-premium`],
    path: config.bootcamp_path,
    continuousLoop: config.continuous_improvement_policy,
    graduationRule: "All required held-out, regression, safety, privacy, rights, cost, and rollback gates must pass. Time spent is not graduation evidence.",
  }));
  const gateCoverage = Object.fromEntries(config.readiness_gates.map((gate) => {
    const key = gate.id === "source_linked" ? "sourceLinked"
      : gate.id === "setup_path_ready" ? "setupPathReady"
        : gate.id === "exact_version_verified" ? "exactVersionVerified"
          : gate.id === "adapter_sandbox_passed" ? "adapterSandboxPassed"
            : gate.id === "live_benchmark_passed" ? "liveBenchmarkPassed"
              : gate.id;
    return [gate.id, connections.filter((item) => item.checks[key as keyof typeof item.checks]).length];
  }));

  return {
    schema: config.schema,
    version: config.version,
    reviewedOn: config.reviewed_on,
    mission: config.mission,
    truthContract: config.truth_contract,
    councilPolicy: config.council_policy,
    readinessGates: config.readiness_gates,
    summary: {
      modelTargets: connections.length,
      providerSources: benchmarkCatalog.summary.providers,
      taskCategories: MODEL_DISCOVERY_TASKS.length,
      councils: councils.length,
      seatsPerCouncil: config.council_policy.seats_per_task,
      datasetPackageTemplates: packages.length,
      benchmarkRoadmaps: benchmarkRoadmaps.length,
      bootcampTracks: bootcampTracks.length,
      catalogReady: connections.filter((item) => item.checks.cataloged).length,
      categorized: connections.filter((item) => item.checks.categorized).length,
      sourceLinked: connections.filter((item) => item.checks.sourceLinked).length,
      setupPathsReady: connections.filter((item) => item.checks.setupPathReady).length,
      exactVersionsVerified: connections.filter((item) => item.checks.exactVersionVerified).length,
      adapterSandboxesPassed: connections.filter((item) => item.checks.adapterSandboxPassed).length,
      liveConnected: connections.filter((item) => item.liveProviderConnection).length,
      liveBenchmarked: connections.filter((item) => item.liveBenchmarkEvidence).length,
      datasetRecordsIncluded: 0,
      verifiedRevenueProduced: 0,
    },
    gateCoverage,
    taskCategories: MODEL_DISCOVERY_TASKS,
    connections,
    councils,
    benchmarkRoadmaps,
    bootcampTracks,
    datasetPackages: packages,
    datasetPackagePolicy: config.dataset_package_policy,
    repositoryDatasetInventory: {
      dataFilesDiscovered: 0,
      packageProgramDefinitions: [
        "config/data-discovery-bot-program.json",
        "config/data-package-maximal-testing-program.json",
        "config/universal-model-training-library-data-pack-program.json",
      ],
      note: "No CSV, JSONL, Parquet, or Arrow training datasets are stored in the repository. The 50 entries are rights-safe package templates, not populated datasets.",
    },
    continuousImprovementPolicy: config.continuous_improvement_policy,
    workstreams: config.workstreams,
    opportunityExperimentPolicy: {
      source: "config/autonomous-bot-business-owner-program.json",
      stages: ["problem discovery", "demand evidence", "offer prototype", "pricing sandbox", "fulfillment test", "owner-approved outreach", "customer outcome measurement", "repeatability review"],
      status: "sandbox_only_until_approved_adapters_and_real_customer_evidence_exist",
      incomeGuaranteed: false,
      paidOrExternalActionRequiresExactApproval: true,
    },
  };
}

function serialized(value: unknown) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

const catalog = buildCatalog();
const json = serialized(catalog);
const publicCatalog = {
  ...catalog,
  connections: catalog.connections.map((item) => ({
    targetId: item.targetId,
    primaryTaskCategory: item.primaryTaskCategory,
    tier: item.tier,
    completionPercent: item.completionPercent,
    gaps: item.gaps,
  })),
  bootcampPath: config.bootcamp_path,
  bootcampTracks: catalog.bootcampTracks.map(({ path: _path, continuousLoop: _loop, ...item }) => item),
  datasetPackages: catalog.datasetPackages.map((item) => ({
    id: item.id,
    name: item.name,
    taskCategory: item.taskCategory,
    packageType: item.packageType,
    intendedUse: item.intendedUse,
    status: item.status,
    recordsIncluded: item.recordsIncluded,
    sellableVerified: item.sellableVerified,
    benchmarkSuites: item.benchmarkSuites,
    nextGate: item.nextGate,
  })),
};
const script = `window.BUDDY_MODEL_PROGRESS_CENTER = ${JSON.stringify(publicCatalog)};\n`;
const checkOnly = process.argv.includes("--check");

if (checkOnly) {
  for (const [path, expected] of [[outputPath, json], [publicPath, script]] as const) {
    if (readFileSync(path, "utf8") !== expected) throw new Error(`Generated file is stale: ${path}`);
  }
  console.log(JSON.stringify(catalog.summary));
} else {
  writeFileSync(outputPath, json);
  writeFileSync(publicPath, script);
  console.log(JSON.stringify(catalog.summary));
}
