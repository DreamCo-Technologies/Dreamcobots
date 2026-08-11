import {
  MODEL_BENCHMARK_TARGETS,
  MODEL_DISCOVERY_TASKS,
} from "./model-benchmark-targets";
import {
  buildModelConnectionSetupPath,
  MODEL_PROVIDER_SOURCE_PROFILES,
  type ModelConnectionKind,
} from "./model-provider-sources";

const ACCOUNT_REQUIRED_KINDS = new Set<ModelConnectionKind>([
  "api_adapter",
  "account_handoff",
]);

const PROTECTED_SIGNUP_GATES = [
  "current terms and privacy review",
  "email or phone verification",
  "CAPTCHA or anti-abuse challenge",
  "identity or business verification when required",
  "MFA, passkey, and recovery setup",
  "plan, fee, tax, and payment review",
] as const;

function unique(values: string[]) {
  return [...new Set(values.filter(Boolean))];
}

function efficiencyGuidance(connectionKind: ModelConnectionKind) {
  if (connectionKind === "local_runtime") {
    return [
      "Use one pinned local runtime for every compatible target instead of duplicating model installs.",
      "Benchmark hardware fit, latency, memory, quality, license, and energy cost before assigning production work.",
      "Keep model weights and generated data local unless the owner approves a specific transfer.",
    ];
  }
  if (connectionKind === "open_source_sandbox") {
    return [
      "Start from the official repository in a network-off sandbox and pin the reviewed commit and license.",
      "Reuse one isolated toolchain for compatible targets while keeping each benchmark and permission scope separate.",
      "Promote only after dependency, security, quality, rollback, and held-out capability checks pass.",
    ];
  }
  if (connectionKind === "api_adapter") {
    return [
      "Use one provider account and one least-privilege credential reference for every approved target on that provider.",
      "Route by measured task quality, latency, reliability, privacy, and cost; never by catalog position alone.",
      "Set spend limits, test in a provider sandbox, pin exact model IDs, and keep automatic paid upgrades off.",
    ];
  }
  return [
    "Use one official provider account for every approved target covered by that account.",
    "Enable MFA, keep recovery details owner-controlled, and grant only the minimum workspace access.",
    "Verify task quality and current plan limits before treating the product as an active Buddy route.",
  ];
}

function setupSteps(connectionKind: ModelConnectionKind) {
  if (connectionKind === "local_runtime") {
    return [
      "Review the official source, current license, hardware requirements, and exact release.",
      "Install or select the runtime in an isolated local sandbox.",
      "Run the assigned benchmark fixtures and record versioned evidence.",
      "Enable the route only after resource limits and rollback are verified.",
    ];
  }
  if (connectionKind === "open_source_sandbox") {
    return [
      "Review the official repository, license, release, dependencies, and security notices.",
      "Prepare a network-off sandbox with pinned dependencies and explicit resource limits.",
      "Run security, capability, regression, privacy, and rollback checks.",
      "Approve any network, credential, write, publish, or paid access separately.",
    ];
  }
  return [
    "Open the official provider source and review current plans, terms, regions, and account requirements.",
    "Complete protected signup steps in the provider's own page with the owner present.",
    "Store only a scoped credential reference in an approved keychain or vault.",
    "Run an exact-model adapter probe and task benchmark before enabling the route.",
  ];
}

export function buildResourceOnboardingCatalog() {
  return MODEL_PROVIDER_SOURCE_PROFILES.map((profile) => {
    const targets = MODEL_BENCHMARK_TARGETS.filter((target) => target.provider === profile.provider);
    const curatedTargets = targets.filter((target) => !target.discoveryTarget);
    const discoveryTargets = targets.filter((target) => target.discoveryTarget);
    const declaredFreeTargetCount = curatedTargets.filter((target) => ["free", "freemium"].includes(target.tier)).length;
    const declaredPaidTargetCount = curatedTargets.filter((target) => ["paid", "freemium"].includes(target.tier)).length;
    const noAccountSetup = !ACCOUNT_REQUIRED_KINDS.has(profile.connectionKind);
    const curatedStrengths = unique(curatedTargets.map((target) => target.bestFor)).slice(0, 6);
    const curatedTaskCategories = unique(curatedTargets.map((target) => target.category));
    const discoveryTaskCoverage = unique(discoveryTargets.map((target) => target.category))
      .filter((task) => MODEL_DISCOVERY_TASKS.includes(task as (typeof MODEL_DISCOVERY_TASKS)[number]));

    return {
      provider: profile.provider,
      officialSource: profile.officialSource,
      sourceKind: profile.sourceKind,
      reviewedOn: profile.reviewedOn,
      connectionKind: profile.connectionKind,
      connectorId: profile.connectorId,
      setupPath: buildModelConnectionSetupPath(profile),
      targetCount: targets.length,
      curatedTargetCount: curatedTargets.length,
      discoveryTargetCount: discoveryTargets.length,
      curatedTaskCategories,
      curatedStrengths,
      discoveryTaskCoverage,
      bestUseSummary: curatedStrengths.length
        ? curatedStrengths.slice(0, 2).join("; ")
        : "Official-catalog discovery only. Verify exact models with comparable benchmarks before assigning work.",
      access: {
        declaredFreeTargetCount,
        declaredPaidTargetCount,
        localOrOpenSourceRoute: noAccountSetup,
        currentPricingVerified: false,
        freeUseGuaranteed: false,
        paidUseApproved: false,
        label: noAccountSetup
          ? "No provider account required for the initial local or sandbox setup"
          : declaredFreeTargetCount && declaredPaidTargetCount
            ? "Declared free and paid options; verify current limits"
            : declaredFreeTargetCount
              ? "Declared free option; verify current limits"
              : declaredPaidTargetCount
                ? "Declared paid option; no spending approved"
                : "Current access and price must be verified",
      },
      accountRequired: !noAccountSetup,
      userPresenceRequired: !noAccountSetup,
      automaticSubmission: false,
      rawCredentialsAccepted: false,
      protectedSignupGates: noAccountSetup ? [] : [...PROTECTED_SIGNUP_GATES],
      efficiencyGuidance: efficiencyGuidance(profile.connectionKind),
      setupSteps: setupSteps(profile.connectionKind),
      liveProviderConnection: false,
      liveBenchmarkPassed: false,
    };
  });
}

export type ResourceOnboardingProvider = ReturnType<typeof buildResourceOnboardingCatalog>[number];
