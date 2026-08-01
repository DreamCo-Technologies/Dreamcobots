import { createHash, randomUUID } from "node:crypto";

import { z } from "zod";

export const deviceActionPlanRequestSchema = z.object({
  objective: z.string().trim().min(5).max(1_000),
  deviceType: z.enum(["desktop", "phone", "tablet", "tv", "browser", "server", "other"]),
  appName: z.string().trim().min(2).max(80),
  actionMode: z.enum(["observe", "draft", "preview", "execute"]).default("preview"),
  requestedActions: z.array(z.string().trim().min(2).max(160)).min(1).max(20),
  connectorId: z.string().trim().regex(/^[A-Za-z0-9_.:-]{2,80}$/).optional(),
  requestedScopes: z.array(z.string().trim().regex(/^[A-Za-z0-9._:/-]{1,80}$/)).max(40).default([]),
  exactApprovalForThisPlan: z.boolean().default(false),
}).strict();

export function createDeviceActionPlan(
  input: z.infer<typeof deviceActionPlanRequestSchema>,
) {
  const request = deviceActionPlanRequestSchema.parse(input);
  const fingerprint = createHash("sha256")
    .update(`${request.deviceType}:${request.appName}:${request.objective}`)
    .digest("hex")
    .slice(0, 20);
  const executeRequested = request.actionMode === "execute";

  return {
    schema: "dreamco.buddy_device_action_plan.v1",
    planId: `device-plan-${randomUUID()}`,
    fingerprint,
    status: executeRequested ? "live_adapter_and_action_approval_required" : "sandbox_plan_ready",
    target: {
      deviceType: request.deviceType,
      appName: request.appName,
      connectorId: request.connectorId ?? null,
    },
    objective: request.objective,
    actionMode: request.actionMode,
    requestedActions: request.requestedActions,
    requestedScopes: [...new Set(request.requestedScopes)],
    exactApprovalRecordedForPlan: request.exactApprovalForThisPlan,
    executionPermittedByThisPlanner: false,
    automaticDeviceTakeover: false,
    rawCredentialsAccepted: false,
    controls: {
      leastPrivilege: true,
      readOnlyFirst: true,
      sandboxBeforeLive: true,
      previewBeforeWrite: true,
      oneActionApproval: true,
      visibleActionLog: true,
      pauseAndStopAlwaysAvailable: true,
      userPresenceForSigninPaymentAndLegalConsent: true,
    },
    steps: [
      "Connect the official app or device adapter with the minimum scopes.",
      "Run the requested actions against synthetic or owner-approved sandbox data.",
      "Show the exact clicks, fields, recipients, files, and expected side effects in a preview.",
      "Request one-action approval for every live write, send, purchase, signup, or publication.",
      "Execute through the authenticated adapter and write a redacted audit receipt.",
    ],
    liveExternalActionTaken: false,
  } as const;
}
