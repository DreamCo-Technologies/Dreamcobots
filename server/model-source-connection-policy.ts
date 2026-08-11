import { MODEL_BENCHMARK_TARGETS } from "@shared/model-benchmark-targets";
import {
  buildModelConnectionSetupPath,
  getModelProviderSource,
  MODEL_PROVIDER_SOURCE_PROFILES,
} from "@shared/model-provider-sources";
import { buildResourceOnboardingCatalog } from "@shared/resource-onboarding";
import { z } from "zod";

import { getBuddyModelRouterConfig } from "./buddy-model-policy";

export const resourceOnboardingPlanRequestSchema = z.object({
  objective: z.string().trim().min(5).max(500),
  providers: z.array(z.string().trim().min(2).max(80)).max(100).default([]),
  accessMode: z.enum(["free_first", "include_paid_options"]).default("free_first"),
  queueMode: z.enum(["guided_one_at_a_time", "prepare_provider_queue"]).default("guided_one_at_a_time"),
  batchSize: z.number().int().min(1).max(10).default(3),
}).strict();

function connectorConfigured(
  connector: ReturnType<typeof getBuddyModelRouterConfig>["connectors"][number] | undefined,
  environment: NodeJS.ProcessEnv,
) {
  if (!connector) return false;
  if (connector.availability === "always") return true;
  return connector.secret_references.some((reference) => Boolean(environment[reference]?.trim()));
}

function connectionStatus(
  profile: NonNullable<ReturnType<typeof getModelProviderSource>>,
  connector: ReturnType<typeof getBuddyModelRouterConfig>["connectors"][number] | undefined,
  configured: boolean,
) {
  if (profile.connectorId === "buddy_native" && connector?.implementation_status === "local_ready") {
    return "local_route_ready";
  }
  if (profile.connectionKind === "account_handoff") return "user_connection_required";
  if (profile.connectionKind === "open_source_sandbox" && !profile.connectorId) return "sandbox_install_required";
  if (!connector) return "adapter_contract_required";
  if (!configured) return "configuration_required";
  if (connector.implementation_status === "contract_only") return "adapter_test_required";
  return "exact_model_probe_required";
}

export function getModelSourceConnectionAudit(environment: NodeJS.ProcessEnv = process.env) {
  const router = getBuddyModelRouterConfig();
  const connectorById = new Map(router.connectors.map((connector) => [connector.id, connector]));
  const targets = MODEL_BENCHMARK_TARGETS.map((target) => {
    const profile = getModelProviderSource(target.provider);
    if (!profile) throw new Error(`Missing source connection profile for ${target.provider}`);
    const connector = profile.connectorId ? connectorById.get(profile.connectorId) : undefined;
    if (profile.connectorId && !connector) {
      throw new Error(`Missing router connector ${profile.connectorId} for ${target.provider}`);
    }
    const configured = connectorConfigured(connector, environment);
    const status = connectionStatus(profile, connector, configured);
    return {
      targetId: target.id,
      name: target.name,
      provider: target.provider,
      targetKind: target.discoveryTarget ? "official_catalog_discovery" : "curated_competitor_profile",
      officialSource: profile.officialSource,
      sourceKind: profile.sourceKind,
      sourceReviewedOn: profile.reviewedOn,
      sourceLinked: true,
      connectionKind: profile.connectionKind,
      connectorId: profile.connectorId,
      connectorContractPresent: Boolean(connector) || ["account_handoff", "open_source_sandbox"].includes(profile.connectionKind),
      credentialReferenceConfigured: configured,
      setupPath: buildModelConnectionSetupPath(profile),
      setupPathReady: true,
      status,
      exactModelId: target.exactModelId,
      exactModelIdVerified: false,
      liveProbePassed: false,
      liveProviderConnection: false,
    };
  });

  const providerConnections = MODEL_PROVIDER_SOURCE_PROFILES.map((profile) => {
    const connector = profile.connectorId ? connectorById.get(profile.connectorId) : undefined;
    const configured = connectorConfigured(connector, environment);
    const providerTargets = targets.filter((target) => target.provider === profile.provider);
    return {
      provider: profile.provider,
      targetCount: providerTargets.length,
      officialSource: profile.officialSource,
      sourceKind: profile.sourceKind,
      connectionKind: profile.connectionKind,
      connectorId: profile.connectorId,
      connectorContractPresent: providerTargets.every((target) => target.connectorContractPresent),
      credentialReferenceConfigured: configured,
      setupPath: buildModelConnectionSetupPath(profile),
      status: providerTargets[0]?.status || "no_targets",
      liveProbePassed: false,
    };
  });

  return {
    schema: "dreamco.buddy_model_source_connections.v1",
    generatedAt: new Date().toISOString(),
    summary: {
      targets: targets.length,
      providerProfiles: providerConnections.length,
      sourceLinkedTargets: targets.filter((target) => target.sourceLinked).length,
      setupPathTargets: targets.filter((target) => target.setupPathReady).length,
      connectorContractTargets: targets.filter((target) => target.connectorContractPresent).length,
      credentialConfiguredTargets: targets.filter((target) => target.credentialReferenceConfigured).length,
      localReadyTargets: targets.filter((target) => target.status === "local_route_ready").length,
      liveVerifiedTargets: targets.filter((target) => target.liveProviderConnection).length,
    },
    truthContract: {
      sourceLinkedMeansLiveConnected: false,
      setupPathMeansAdapterImplemented: false,
      credentialConfiguredMeansModelVerified: false,
      liveRequiresExactModelIdAdapterProbeAndBenchmarkEvidence: true,
      rawCredentialsReturned: false,
    },
    providerConnections,
    targets,
  } as const;
}

export function getResourceOnboardingCatalog(environment: NodeJS.ProcessEnv = process.env) {
  const audit = getModelSourceConnectionAudit(environment);
  const auditByProvider = new Map(audit.providerConnections.map((provider) => [provider.provider, provider]));
  const providers = buildResourceOnboardingCatalog().map((provider) => {
    const connection = auditByProvider.get(provider.provider);
    return {
      ...provider,
      credentialReferenceConfigured: Boolean(connection?.credentialReferenceConfigured),
      connectionStatus: connection?.status || "configuration_required",
      liveProviderConnection: Boolean(connection?.liveProbePassed),
    };
  });
  const accountProviders = providers.filter((provider) => provider.accountRequired);
  const noAccountProviders = providers.filter((provider) => !provider.accountRequired);

  return {
    schema: "dreamco.resource_onboarding_catalog.v1",
    generatedAt: new Date().toISOString(),
    summary: {
      resourceTargets: MODEL_BENCHMARK_TARGETS.length,
      uniqueProviders: providers.length,
      providerAccountMaximum: accountProviders.length,
      noAccountProviderSetups: noAccountProviders.length,
      configuredCredentialReferences: providers.filter((provider) => provider.credentialReferenceConfigured).length,
      liveVerifiedProviders: providers.filter((provider) => provider.liveProviderConnection).length,
      automaticAccountSubmissions: 0,
    },
    truthContract: {
      fiveHundredTargetsMeanFiveHundredAccounts: false,
      oneProviderAccountMayCoverMultipleTargets: true,
      queuePreparationCreatesAccounts: false,
      openingOfficialSourceCreatesAccount: false,
      credentialReferenceMeansLiveVerified: false,
      protectedSignupStepsRequireUserPresence: true,
      paidSignupOrUsageRequiresLaterExactApproval: true,
      rawCredentialsReturned: false,
    },
    providers,
  } as const;
}

function chunks<T>(items: T[], size: number) {
  const output: T[][] = [];
  for (let index = 0; index < items.length; index += size) output.push(items.slice(index, index + size));
  return output;
}

export function createResourceOnboardingPlan(
  requestInput: z.input<typeof resourceOnboardingPlanRequestSchema>,
  environment: NodeJS.ProcessEnv = process.env,
) {
  const request = resourceOnboardingPlanRequestSchema.parse(requestInput);
  const catalog = getResourceOnboardingCatalog(environment);
  const byName = new Map(catalog.providers.map((provider) => [provider.provider.toLowerCase(), provider]));
  const requested = request.providers.length
    ? request.providers.map((name) => {
      const provider = byName.get(name.toLowerCase());
      if (!provider) throw new Error(`Unknown resource provider: ${name}`);
      return provider;
    })
    : [...catalog.providers];
  const uniqueProviders = [...new Map(requested.map((provider) => [provider.provider, provider])).values()];
  const priority = (provider: (typeof catalog.providers)[number]) => {
    if (!provider.accountRequired) return 0;
    if (provider.access.declaredFreeTargetCount > 0) return 1;
    if (provider.credentialReferenceConfigured) return 2;
    return 3;
  };
  const ordered = uniqueProviders.sort((left, right) => priority(left) - priority(right) || left.provider.localeCompare(right.provider));
  const queue = ordered.map((provider, index) => {
    const paidChoiceHeld = request.accessMode === "free_first"
      && provider.accountRequired
      && provider.access.declaredFreeTargetCount === 0;
    return {
      position: index + 1,
      provider: provider.provider,
      targetCount: provider.targetCount,
      setupPath: provider.setupPath,
      officialSource: provider.officialSource,
      accountRequired: provider.accountRequired,
      actionType: provider.accountRequired ? "user_present_provider_handoff" : "local_or_open_source_setup",
      status: provider.liveProviderConnection
        ? "already_live_verified"
        : paidChoiceHeld
          ? "held_for_paid_option_review"
          : provider.accountRequired
            ? "ready_for_user_handoff"
            : "ready_for_sandbox_setup",
      currentPricingVerified: false,
      paidUseApproved: false,
      automaticSubmission: false,
      userPresenceRequired: provider.userPresenceRequired,
      efficiencyGuidance: provider.efficiencyGuidance,
      nextAction: paidChoiceHeld
        ? "Review the current plan and price. Enabling paid access still needs separate exact approval."
        : provider.setupSteps[0],
    };
  });
  const batches = chunks(queue, request.batchSize).map((providers, index) => ({
    batch: index + 1,
    providers,
    maximumConcurrentUserHandoffs: 1,
  }));
  const ready = queue.find((provider) => ["ready_for_user_handoff", "ready_for_sandbox_setup"].includes(provider.status));

  return {
    schema: "dreamco.resource_onboarding_plan.v1",
    createdAt: new Date().toISOString(),
    objective: request.objective,
    accessMode: request.accessMode,
    queueMode: request.queueMode,
    summary: {
      resourceTargetsCovered: queue.reduce((total, provider) => total + provider.targetCount, 0),
      uniqueProvidersQueued: queue.length,
      maximumProviderAccounts: queue.filter((provider) => provider.accountRequired).length,
      noAccountSetups: queue.filter((provider) => !provider.accountRequired).length,
      heldForPaidReview: queue.filter((provider) => provider.status === "held_for_paid_option_review").length,
      accountsCreated: 0,
      formsSubmitted: 0,
      paymentsMade: 0,
      liveConnectionsProven: queue.filter((provider) => provider.status === "already_live_verified").length,
    },
    nextAction: ready
      ? { provider: ready.provider, setupPath: ready.setupPath, instruction: ready.nextAction }
      : null,
    batches,
    boundaries: {
      onlyOneProtectedSignupOpenAtATime: true,
      automaticFormSubmission: false,
      automaticTermsAcceptance: false,
      automaticCaptchaOrIdentityCompletion: false,
      automaticPaidPlanSelection: false,
      rawCredentialsAccepted: false,
      exactApprovalRequiredForEveryExternalWriteOrPurchase: true,
    },
  } as const;
}
