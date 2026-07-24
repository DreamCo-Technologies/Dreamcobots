import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

type ModelConnector = {
  id: string;
  label: string;
  mode: "free" | "premium";
  protocol: string;
  availability: string;
  secret_references: string[];
  task_types: string[];
};

type ModelRouterConfig = {
  schema: string;
  default_mode: "free";
  policy: Record<string, boolean>;
  connectors: ModelConnector[];
};

export const buddyModelRequestSchema = z.object({
  modelMode: z.enum(["free", "premium"]).default("free"),
  modelConnectorId: z.string().trim().regex(/^[a-z0-9_]{2,64}$/).optional(),
  selectedModelId: z.string().trim().regex(/^[A-Za-z0-9_.:/-]{1,120}$/).optional(),
  approvePaidModelForThisRequest: z.boolean().default(false),
}).strict();

export type BuddyModelRequest = z.infer<typeof buddyModelRequestSchema>;

let configCache: ModelRouterConfig | undefined;

export function getBuddyModelRouterConfig(
  path = resolve(process.cwd(), "config", "buddy-model-router.json"),
) {
  configCache ??= JSON.parse(readFileSync(path, "utf8")) as ModelRouterConfig;
  return configCache;
}

function isConfigured(connector: ModelConnector, environment: NodeJS.ProcessEnv) {
  if (connector.availability === "always") return true;
  return connector.secret_references.some((reference) => Boolean(environment[reference]?.trim()));
}

export function resolveBuddyModelPlan(
  requestInput: z.input<typeof buddyModelRequestSchema>,
  environment: NodeJS.ProcessEnv = process.env,
) {
  const request = buddyModelRequestSchema.parse(requestInput);
  const config = getBuddyModelRouterConfig();
  const eligible = config.connectors.filter((connector) => connector.mode === request.modelMode);
  const requested = request.modelConnectorId
    ? config.connectors.find((connector) => connector.id === request.modelConnectorId)
    : undefined;

  if (request.modelConnectorId && !requested) {
    throw new Error(`Unknown model connector: ${request.modelConnectorId}`);
  }
  if (requested && requested.mode !== request.modelMode) {
    throw new Error(`${requested.label} is not available in ${request.modelMode} mode`);
  }

  const connector = requested
    || eligible.find((candidate) => isConfigured(candidate, environment))
    || eligible[0];
  if (!connector) throw new Error(`No ${request.modelMode} model route is configured`);

  const configured = isConfigured(connector, environment);
  const paidApprovalRequired = request.modelMode === "premium" && !request.approvePaidModelForThisRequest;
  const status = request.modelMode === "free"
    ? configured ? "free_route_ready" : "configuration_required"
    : paidApprovalRequired
      ? "paid_approval_required"
      : configured
        ? "provider_adapter_ready"
        : "configuration_required";

  return {
    schema: "dreamco.buddy_model_plan.v1",
    mode: request.modelMode,
    connector: {
      id: connector.id,
      label: connector.label,
      protocol: connector.protocol,
      configured,
      taskTypes: connector.task_types,
    },
    selectedModelId: request.selectedModelId || "provider_default_for_task",
    status,
    paidUseApprovedForThisRequest:
      request.modelMode === "premium" && request.approvePaidModelForThisRequest,
    automaticPaidUpgrade: false,
    freeFallback: "buddy_native",
    providerCallExecuted: false,
    nextStep: status === "paid_approval_required"
      ? "Approve premium use for this one request or switch back to free."
      : status === "configuration_required"
        ? "Connect the selected provider with a backend secret reference."
        : request.modelMode === "premium"
          ? "The authenticated provider adapter may execute this approved request."
          : "Buddy Native will prepare the response locally without a provider charge.",
  } as const;
}
