import { MODEL_BENCHMARK_TARGETS } from "@shared/model-benchmark-targets";
import {
  buildModelConnectionSetupPath,
  getModelProviderSource,
  MODEL_PROVIDER_SOURCE_PROFILES,
} from "@shared/model-provider-sources";

import { getBuddyModelRouterConfig } from "./buddy-model-policy";

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
