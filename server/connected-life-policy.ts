import { createHash, randomUUID } from "node:crypto";

import { z } from "zod";

export const APP_CATEGORIES = [
  "social", "communication", "creative", "business", "finance", "commerce", "developer",
  "education", "health", "home", "travel", "government", "files", "custom",
] as const;

export const APP_ACTIONS = [
  "catalog", "read", "compare", "draft", "schedule", "publish", "send", "change_account",
  "cancel_subscription", "submit_privacy_request", "pay", "transfer", "license_data",
] as const;

const HIGH_IMPACT_ACTIONS = new Set<string>([
  "publish", "send", "change_account", "cancel_subscription", "submit_privacy_request",
  "pay", "transfer", "license_data",
]);

const opaqueReferenceSchema = z.string().trim().regex(/^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$/);

export const appConnectionPlanRequestSchema = z.object({
  appName: z.string().trim().min(2).max(120),
  officialUrl: z.string().url().max(2_048),
  category: z.enum(APP_CATEGORIES),
  groupName: z.string().trim().min(2).max(80),
  authMethod: z.enum(["oauth_pkce", "oauth_device", "api_key_reference", "browser_handoff", "custom_rest"]),
  accessLevel: z.enum(["catalog_only", "read_selected", "draft_only", "approved_actions"]),
  requestedActions: z.array(z.enum(APP_ACTIONS)).min(1).max(APP_ACTIONS.length),
  requestedDataCategories: z.array(z.string().trim().regex(/^[a-z][a-z0-9_]{1,63}$/)).max(40).default([]),
  retentionDays: z.number().int().min(1).max(365).default(30),
  ownerAuthorized: z.boolean(),
  secretReference: opaqueReferenceSchema.optional(),
}).strict();

export const appGroupWorkflowPlanRequestSchema = z.object({
  groupName: z.string().trim().min(2).max(80),
  objective: z.string().trim().min(10).max(1_000),
  appPlanIds: z.array(opaqueReferenceSchema).min(2).max(50),
  actions: z.array(z.enum(APP_ACTIONS)).min(1).max(APP_ACTIONS.length),
  ownerApprovedSandbox: z.boolean(),
}).strict();

export const socialWorkspacePlanRequestSchema = z.object({
  platform: z.string().trim().min(2).max(80),
  accountReference: z.string().trim().regex(/^social-account:[A-Za-z0-9_.:/-]{2,100}$/),
  objective: z.string().trim().min(10).max(1_000),
  mode: z.enum(["draft", "schedule", "publish_once", "live_rehearsal", "live_show"]),
  contentTypes: z.array(z.enum(["text", "image", "video", "music", "story", "short", "livestream"])).min(1).max(7),
  syntheticMedia: z.boolean().default(false),
  mediaRightsConfirmed: z.boolean().default(false),
  adultSubjectConsentConfirmed: z.boolean().default(false),
  ownerAuthorizedAccount: z.boolean(),
  moderationEnabled: z.boolean().default(true),
}).strict();

const moneySchema = z.string().trim().regex(/^\d{1,9}(?:\.\d{1,2})?$/);
const currencySchema = z.string().trim().regex(/^[A-Za-z]{3}$/).transform((value) => value.toUpperCase());
const subscriptionSchema = z.object({
  id: opaqueReferenceSchema,
  merchant: z.string().trim().min(2).max(120),
  amount: moneySchema,
  currency: currencySchema,
  cadence: z.enum(["weekly", "monthly", "quarterly", "annual"]),
  renewalAt: z.string().datetime(),
  cancellationUrl: z.string().url().max(2_048).optional(),
}).strict();
const billSchema = z.object({
  id: opaqueReferenceSchema,
  payee: z.string().trim().min(2).max(120),
  amount: moneySchema,
  currency: currencySchema,
  dueAt: z.string().datetime(),
  accountReference: opaqueReferenceSchema,
}).strict();

export const financeWorkspacePlanRequestSchema = z.object({
  subscriptions: z.array(subscriptionSchema).max(500).default([]),
  bills: z.array(billSchema).max(500).default([]),
  monthlyBudget: moneySchema.optional(),
  budgetCurrency: currencySchema.default("USD"),
}).strict();

function safeOfficialUrl(raw: string) {
  const url = new URL(raw);
  if (url.protocol !== "https:" || url.username || url.password) {
    throw new Error("Use a credential-free official HTTPS URL.");
  }
  return url;
}

function fingerprint(value: string) {
  return createHash("sha256").update(value).digest("hex").slice(0, 20);
}

export function createAppConnectionPlan(input: z.infer<typeof appConnectionPlanRequestSchema>) {
  const request = appConnectionPlanRequestSchema.parse(input);
  if (!request.ownerAuthorized) throw new Error("The owner must authorize this app connection.");
  const url = safeOfficialUrl(request.officialUrl);
  const actions = [...new Set(request.requestedActions)];
  const highImpactActions = actions.filter((action) => HIGH_IMPACT_ACTIONS.has(action));
  if (request.accessLevel === "catalog_only" && actions.some((action) => action !== "catalog")) {
    throw new Error("Catalog-only apps cannot request data or action permissions.");
  }
  if (request.authMethod === "api_key_reference" && !request.secretReference) {
    throw new Error("API-key connections require a vault reference, never a raw key.");
  }
  return {
    schema: "dreamco.buddy_app_connection_plan.v1",
    planId: `app-plan-${randomUUID()}`,
    status: request.accessLevel === "catalog_only" ? "cataloged" : "authentication_handoff_required",
    app: {
      name: request.appName,
      officialOrigin: url.origin,
      officialPath: url.pathname,
      category: request.category,
      groupName: request.groupName,
    },
    connection: {
      authMethod: request.authMethod,
      accessLevel: request.accessLevel,
      actions,
      dataCategories: [...new Set(request.requestedDataCategories)],
      retentionDays: request.retentionDays,
      secretReferenceFingerprint: request.secretReference ? fingerprint(request.secretReference) : null,
      rawCredentialsAccepted: false,
      connected: false,
    },
    approvalGates: [
      "review exact scopes on the provider domain",
      "run read-only sandbox and connection health checks",
      ...(highImpactActions.length ? ["fresh approval for every high-impact action"] : []),
    ],
    highImpactActions,
  } as const;
}

export function createAppGroupWorkflowPlan(input: z.infer<typeof appGroupWorkflowPlanRequestSchema>) {
  const request = appGroupWorkflowPlanRequestSchema.parse(input);
  if (!request.ownerApprovedSandbox) throw new Error("Grouped workflows require an owner-approved sandbox first.");
  const actions = [...new Set(request.actions)];
  return {
    schema: "dreamco.buddy_app_group_workflow_plan.v1",
    workflowId: `app-workflow-${randomUUID()}`,
    status: "sandbox_plan_ready",
    groupName: request.groupName,
    objective: request.objective,
    appPlanIds: [...new Set(request.appPlanIds)],
    actions,
    highImpactActions: actions.filter((action) => HIGH_IMPACT_ACTIONS.has(action)),
    controls: {
      readOnlyFirst: true,
      leastPrivilegePerApp: true,
      dataJoinRequiresCompatiblePurposeGrants: true,
      previewBeforeWrite: true,
      freshApprovalPerHighImpactAction: true,
      liveActionsTaken: false,
    },
  } as const;
}

export function createSocialWorkspacePlan(input: z.infer<typeof socialWorkspacePlanRequestSchema>) {
  const request = socialWorkspacePlanRequestSchema.parse(input);
  if (!request.ownerAuthorizedAccount) throw new Error("The owner must authorize the selected social account.");
  if (request.syntheticMedia && (!request.mediaRightsConfirmed || !request.adultSubjectConsentConfirmed)) {
    throw new Error("Synthetic owner or performer media requires confirmed rights and adult subject consent.");
  }
  if (["live_rehearsal", "live_show"].includes(request.mode) && !request.contentTypes.includes("livestream")) {
    throw new Error("Live modes require livestream content.");
  }
  if (request.mode === "live_show" && !request.moderationEnabled) {
    throw new Error("Live shows require moderation and emergency-stop controls.");
  }
  const externalAction = ["schedule", "publish_once", "live_show"].includes(request.mode);
  return {
    schema: "dreamco.buddy_social_workspace_plan.v1",
    workspaceId: `social-workspace-${randomUUID()}`,
    status: externalAction ? "owner_action_approval_required" : "draft_or_rehearsal_plan_ready",
    platform: request.platform,
    accountReference: request.accountReference,
    objective: request.objective,
    mode: request.mode,
    contentTypes: [...new Set(request.contentTypes)],
    syntheticMediaLabelRequired: request.syntheticMedia,
    controls: [
      "authenticated owner account adapter",
      "draft and preview before publish",
      "platform policy and rate-limit checks",
      "comment, guest, and message moderation",
      "delay, mute, hold, and emergency stop for live mode",
      "one exact approval for schedule, publish, or go-live actions",
    ],
    liveExternalActionTaken: false,
    rawCredentialsAccepted: false,
  } as const;
}

function monthlyAmount(amount: string, cadence: "weekly" | "monthly" | "quarterly" | "annual") {
  const numeric = Number(amount);
  const value = cadence === "weekly" ? numeric * 52 / 12
    : cadence === "quarterly" ? numeric / 3
      : cadence === "annual" ? numeric / 12
        : numeric;
  return Math.round(value * 100) / 100;
}

export function createFinanceWorkspacePlan(input: z.infer<typeof financeWorkspacePlanRequestSchema>) {
  const request = financeWorkspacePlanRequestSchema.parse(input);
  const subscriptions = request.subscriptions.map((item) => ({
    ...item,
    cancellationUrl: item.cancellationUrl ? safeOfficialUrl(item.cancellationUrl).toString() : null,
    normalizedMonthlyAmount: monthlyAmount(item.amount, item.cadence),
  }));
  const duplicateMap = new Map<string, string[]>();
  for (const item of subscriptions) {
    const key = `${item.merchant.trim().toLowerCase()}:${item.amount}:${item.currency}`;
    duplicateMap.set(key, [...(duplicateMap.get(key) || []), item.id]);
  }
  const possibleDuplicates = [...duplicateMap.values()].filter((ids) => ids.length > 1);
  const monthlyTotals = subscriptions.reduce<Record<string, number>>((totals, item) => {
    totals[item.currency] = Math.round(((totals[item.currency] || 0) + item.normalizedMonthlyAmount) * 100) / 100;
    return totals;
  }, {});
  const budget = request.monthlyBudget ? Number(request.monthlyBudget) : null;
  return {
    schema: "dreamco.buddy_finance_workspace_plan.v1",
    workspaceId: `finance-workspace-${randomUUID()}`,
    status: "review_ready_no_money_moved",
    subscriptions,
    bills: request.bills,
    monthlyTotals,
    annualizedTotals: Object.fromEntries(
      Object.entries(monthlyTotals).map(([currency, value]) => [currency, Math.round(value * 1_200) / 100]),
    ),
    possibleDuplicates,
    budget: budget === null ? null : {
      amount: budget,
      currency: request.budgetCurrency,
      remaining: Math.round((budget - (monthlyTotals[request.budgetCurrency] || 0)) * 100) / 100,
    },
    reviewActions: [
      "confirm every merchant and renewal",
      "review possible duplicate or unused services",
      "open the official cancellation or refund route",
      "save cancellation, refund, payment, and dispute receipts",
      "request a one-action payment packet only when the owner chooses to pay",
    ],
    paymentCredentialsStored: false,
    cancellationSubmitted: false,
    paymentExecuted: false,
    financialAdviceOrGuaranteeProvided: false,
  } as const;
}
