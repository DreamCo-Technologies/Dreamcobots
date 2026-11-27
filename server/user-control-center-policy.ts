import { randomUUID } from "node:crypto";
import { z } from "zod";

export const COMPANY_DATA_USE_PURPOSES = [
  "service_delivery", "analytics", "personalization", "targeted_advertising",
  "sale", "sharing", "data_brokerage", "ai_training", "model_evaluation",
  "research", "automated_decisions", "cross_company_profiling",
] as const;

export const USER_DATA_SOURCE_TYPES = [
  "official_account_export", "authorized_connector", "user_upload", "public_web",
  "github_repository", "email", "calendar", "cloud_storage", "documents",
  "database", "api", "photos", "audio", "video", "social_account", "commerce_account",
] as const;

const dataCategories = [
  "profile", "preferences", "app_activity", "purchases", "creative_work",
  "business_records", "financial", "health", "precise_location", "messages",
  "contacts", "voice", "likeness", "government_id", "credentials", "child_data",
] as const;

const httpsUrl = z.string().url().refine((raw) => {
  const url = new URL(raw);
  return url.protocol === "https:" && !url.username && !url.password;
}, "Use an official HTTPS URL without embedded credentials.");

export const companyDataConsentRequestSchema = z.object({
  companyOrController: z.string().trim().min(2).max(160),
  purpose: z.enum(COMPANY_DATA_USE_PURPOSES),
  dataCategories: z.array(z.enum(dataCategories)).min(1).max(dataCategories.length),
  recipientOrRecipientClass: z.string().trim().min(2).max(200),
  retentionDays: z.number().int().min(1).max(3650),
  jurisdiction: z.string().trim().min(2).max(120),
  decision: z.enum(["opt_in", "opt_out", "withdraw"]),
  explicitUserAction: z.literal(true),
  userAuthenticated: z.literal(true),
  policyVersion: z.string().trim().min(1).max(40),
}).strict();

export function createCompanyDataConsentPlan(input: z.infer<typeof companyDataConsentRequestSchema>) {
  const request = companyDataConsentRequestSchema.parse(input);
  return {
    schema: "dreamco.company_data_consent_receipt.v1",
    receiptId: `consent-${randomUUID()}`,
    companyOrController: request.companyOrController,
    purpose: request.purpose,
    dataCategories: [...new Set(request.dataCategories)],
    recipientOrRecipientClass: request.recipientOrRecipientClass,
    retentionDays: request.retentionDays,
    jurisdiction: request.jurisdiction,
    decision: request.decision,
    effectiveInsideDreamCo: request.decision !== "opt_in",
    externalProviderAction: "not_submitted",
    providerConfirmationRequired: request.decision !== "opt_in",
    auditRequired: true,
    createdAt: new Date().toISOString(),
  } as const;
}

export const buddyStudySourceRequestSchema = z.object({
  sourceName: z.string().trim().min(2).max(160),
  sourceType: z.enum(USER_DATA_SOURCE_TYPES),
  sourceUrl: httpsUrl.optional(),
  sourceReference: z.string().trim().min(2).max(1024),
  ownerAuthorized: z.literal(true),
  rightsConfirmed: z.boolean(),
  requestedScopes: z.array(z.string().trim().regex(/^[A-Za-z0-9._:/-]{1,80}$/)).min(1).max(50),
  studyPurposes: z.array(z.enum(["answering", "retrieval", "summarize", "extract_structured", "planning", "workflow_context", "evaluation"])).min(1).max(7),
  trainingOptIn: z.boolean().default(false),
  retentionDays: z.number().int().min(1).max(3650).default(30),
  refreshMode: z.enum(["manual", "scheduled", "webhook", "none"]).default("manual"),
  readOnly: z.literal(true).default(true),
  noAccessControlBypass: z.literal(true),
  noRawCredentials: z.literal(true),
}).strict().superRefine((value, context) => {
  if (["authorized_connector", "official_account_export", "public_web", "github_repository", "email", "calendar", "cloud_storage", "social_account", "commerce_account"].includes(value.sourceType) && !value.sourceUrl) {
    context.addIssue({ code: z.ZodIssueCode.custom, message: "An official HTTPS source URL is required.", path: ["sourceUrl"] });
  }
  if (!value.rightsConfirmed && value.sourceType !== "public_web") {
    context.addIssue({ code: z.ZodIssueCode.custom, message: "Confirm legal rights to access and study this source.", path: ["rightsConfirmed"] });
  }
  if (value.studyPurposes.includes("evaluation") && !value.rightsConfirmed) {
    context.addIssue({ code: z.ZodIssueCode.custom, message: "Evaluation requires confirmed rights.", path: ["rightsConfirmed"] });
  }
});

export function createBuddyStudySourcePlan(input: z.infer<typeof buddyStudySourceRequestSchema>) {
  const request = buddyStudySourceRequestSchema.parse(input);
  return {
    schema: "dreamco.buddy_study_source_plan.v1",
    planId: `study-source-${randomUUID()}`,
    source: { name: request.sourceName, type: request.sourceType, url: request.sourceUrl ?? null, reference: request.sourceReference },
    scopes: [...new Set(request.requestedScopes)],
    studyPurposes: [...new Set(request.studyPurposes)],
    trainingOptIn: request.trainingOptIn,
    refreshMode: request.refreshMode,
    retentionDays: request.retentionDays,
    accessMode: "read_only",
    status: "user_authorized_source_not_yet_connected",
    dataRead: false,
    userCanRevoke: true,
    accessControlBypass: false,
    rawCredentialsCollected: false,
  } as const;
}

export const userSubscriptionControlRequestSchema = z.object({
  provider: z.string().trim().min(2).max(160),
  subscriptionReference: z.string().trim().min(3).max(160),
  accountOwnerId: z.string().trim().min(3).max(160),
  action: z.enum(["view", "disable_auto_renew", "pause", "resume", "cancel", "change_plan"]),
  price: z.number().nonnegative(),
  currency: z.string().trim().regex(/^[A-Z]{3}$/),
  billingInterval: z.enum(["one_time", "weekly", "monthly", "quarterly", "yearly"]),
  nextRenewalAt: z.string().datetime().nullable(),
  exactUserApproval: z.boolean().default(false),
  authenticatedOwner: z.literal(true),
}).strict().superRefine((value, context) => {
  if (value.action !== "view" && !value.exactUserApproval) {
    context.addIssue({ code: z.ZodIssueCode.custom, message: "A fresh explicit approval is required for subscription changes.", path: ["exactUserApproval"] });
  }
});

export function createUserSubscriptionControlPlan(input: z.infer<typeof userSubscriptionControlRequestSchema>) {
  const request = userSubscriptionControlRequestSchema.parse(input);
  return {
    schema: "dreamco.user_subscription_control_plan.v1",
    planId: `subscription-${randomUUID()}`,
    provider: request.provider,
    subscriptionReference: request.subscriptionReference,
    action: request.action,
    price: request.price,
    currency: request.currency,
    billingInterval: request.billingInterval,
    nextRenewalAt: request.nextRenewalAt,
    status: request.action === "view" ? "view_authorized" : "awaiting_provider_execution",
    providerConfirmation: null,
    completed: false,
    userOwnsSubscription: true,
    noPaymentOrCancellationExecuted: true,
  } as const;
}
