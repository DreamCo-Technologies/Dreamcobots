import { createHash, randomUUID } from "node:crypto";

import { z } from "zod";

export const DATA_CATEGORIES = [
  "profile", "preferences", "app_activity", "purchases", "creative_work", "business_records",
  "financial", "health", "precise_location", "messages", "contacts", "voice", "likeness",
  "government_id", "credentials", "child_data",
] as const;

export const SENSITIVE_DATA_CATEGORIES = new Set<string>([
  "financial", "health", "precise_location", "messages", "contacts", "voice", "likeness",
  "government_id", "credentials", "child_data",
]);
const LICENSABLE_DATA_CATEGORIES = new Set<string>(["creative_work", "business_records"]);

export const dataImportPlanRequestSchema = z.object({
  sourceName: z.string().trim().min(2).max(120),
  sourceUrl: z.string().url().max(2_048).optional(),
  acquisition: z.enum(["user_upload", "official_export", "authorized_connector", "public_domain"]),
  categories: z.array(z.enum(DATA_CATEGORIES)).min(1).max(DATA_CATEGORIES.length),
  requestedScopes: z.array(z.string().trim().regex(/^[A-Za-z0-9._:/-]{1,80}$/)).max(40).default([]),
  retentionDays: z.number().int().min(1).max(365).default(30),
  ownerConfirmsAuthority: z.boolean(),
}).strict();

export const privacyRightsPlanRequestSchema = z.object({
  companyName: z.string().trim().min(2).max(160),
  privacyRequestUrl: z.string().url().max(2_048),
  jurisdiction: z.string().trim().min(2).max(120),
  rights: z.array(z.enum(["access", "portability", "delete", "correct", "opt_out_sale_share", "limit_sensitive_use"])).min(1).max(6),
  identityVerificationMethod: z.enum(["company_form", "verified_email", "postal_mail", "other"]),
  exactApprovalToSubmit: z.boolean().default(false),
}).strict();

export const dataPackagePlanRequestSchema = z.object({
  packageName: z.string().trim().min(3).max(160),
  sourceReference: z.string().trim().regex(/^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$/),
  categories: z.array(z.enum(DATA_CATEGORIES)).min(1).max(DATA_CATEGORIES.length),
  ownerCreatedData: z.boolean(),
  resaleRightsConfirmed: z.boolean(),
  containsMinorData: z.boolean().default(false),
  containsThirdPartyPersonalData: z.boolean().default(false),
  deidentified: z.boolean().default(false),
  recipientClass: z.string().trim().min(3).max(160),
  compensationTerms: z.string().trim().min(3).max(500),
  explicitLicenseOptIn: z.boolean(),
}).strict();

export const memoryPreferencePlanRequestSchema = z.object({
  memoryCategories: z.array(z.enum(["preferences", "projects", "decisions", "learning_progress", "accessibility", "language_style"])).max(6),
  retentionDays: z.number().int().min(1).max(365).default(30),
  personalizationEnabled: z.boolean().default(true),
  privateModelTrainingEnabled: z.boolean().default(false),
  explicitPrivateTrainingOptIn: z.boolean().default(false),
  adaptLanguageStyle: z.boolean().default(true),
  personalityTraits: z.object({
    warmth: z.number().min(0).max(1),
    directness: z.number().min(0).max(1),
    patience: z.number().min(0).max(1),
    curiosity: z.number().min(0).max(1),
  }).strict(),
}).strict();

function safeExternalUrl(raw: string) {
  const url = new URL(raw);
  if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash) {
    throw new Error("Use a credential-free official HTTPS URL.");
  }
  return url;
}

export function createDataImportPlan(input: z.infer<typeof dataImportPlanRequestSchema>) {
  const request = dataImportPlanRequestSchema.parse(input);
  const sourceUrl = request.sourceUrl ? safeExternalUrl(request.sourceUrl).toString() : null;
  if (!request.ownerConfirmsAuthority) throw new Error("Confirm that you own or are authorized to connect this data.");
  if (request.acquisition !== "user_upload" && !sourceUrl) throw new Error("This acquisition route requires an official source URL.");
  if (request.categories.includes("credentials")) throw new Error("Credentials belong in the secret broker, not the personal data vault.");
  if (request.categories.includes("child_data")) throw new Error("Child data requires a separate age-appropriate and guardian-reviewed system.");
  return {
    schema: "dreamco.buddy_data_import_plan.v1",
    planId: `data-import-${randomUUID()}`,
    status: request.acquisition === "authorized_connector" ? "connector_configuration_required" : "owner_handoff_required",
    source: { name: request.sourceName, url: sourceUrl, acquisition: request.acquisition },
    categories: [...new Set(request.categories)],
    requestedScopes: [...new Set(request.requestedScopes)],
    retentionDays: request.retentionDays,
    controls: {
      leastPrivilege: true,
      readOnlyFirst: true,
      purposeSpecificConsent: true,
      encryptedReferenceOnly: true,
      rawCredentialsAccepted: false,
      unrelatedDataCollected: false,
    },
    dataImported: false,
  } as const;
}

export function createPrivacyRightsPlan(input: z.infer<typeof privacyRightsPlanRequestSchema>) {
  const request = privacyRightsPlanRequestSchema.parse(input);
  const url = safeExternalUrl(request.privacyRequestUrl);
  return {
    schema: "dreamco.buddy_privacy_rights_plan.v1",
    requestId: `privacy-${randomUUID()}`,
    fingerprint: createHash("sha256").update(`${request.companyName}:${url.hostname}:${request.rights.join(",")}`).digest("hex").slice(0, 20),
    status: request.exactApprovalToSubmit ? "authenticated_submission_adapter_required" : "draft_ready_for_user_review",
    companyName: request.companyName,
    privacyRequestUrl: url.toString(),
    jurisdiction: request.jurisdiction,
    requestedRights: [...new Set(request.rights)],
    identityVerificationMethod: request.identityVerificationMethod,
    identityDocumentsStoredByPlanner: false,
    requestSubmitted: false,
    companyComplianceGuaranteed: false,
    trackingChecklist: [
      "save the submitted request and timestamp",
      "record the company's confirmation and stated deadline",
      "send a user-approved follow-up if the deadline passes",
      "record fulfilled, partially fulfilled, denied, or no-response evidence",
      "show regulator or qualified-counsel escalation resources when applicable",
    ],
  } as const;
}

export function createDataPackagePlan(input: z.infer<typeof dataPackagePlanRequestSchema>) {
  const request = dataPackagePlanRequestSchema.parse(input);
  const categories = [...new Set(request.categories)];
  const sensitive = categories.filter((category) => SENSITIVE_DATA_CATEGORIES.has(category));
  if (!request.ownerCreatedData || !request.resaleRightsConfirmed || !request.explicitLicenseOptIn) {
    throw new Error("Data licensing requires owner-created data, confirmed resale rights, and a separate opt-in.");
  }
  if (request.containsMinorData || request.containsThirdPartyPersonalData || sensitive.length) {
    throw new Error("Sensitive, minor, credential, or third-party personal data cannot be packaged for sale through Buddy.");
  }
  if (categories.some((category) => !LICENSABLE_DATA_CATEGORIES.has(category))) {
    throw new Error("Only rights-cleared creative work and original business datasets may be licensed through Buddy.");
  }
  return {
    schema: "dreamco.buddy_data_package_plan.v1",
    packageId: `data-package-${randomUUID()}`,
    status: "manifest_ready_owner_review_required",
    packageName: request.packageName,
    sourceReferenceFingerprint: createHash("sha256").update(request.sourceReference).digest("hex").slice(0, 20),
    categories,
    deidentified: request.deidentified,
    recipientClass: request.recipientClass,
    compensationTerms: request.compensationTerms,
    manifest: ["dataset card", "field dictionary", "provenance ledger", "license", "quality report", "withdrawal and update policy"],
    rawDataIncludedInPlan: false,
    marketplaceListingCreated: false,
    saleCompleted: false,
    revocableBeforeLicenseExecution: true,
  } as const;
}

export function createMemoryPreferencePlan(input: z.infer<typeof memoryPreferencePlanRequestSchema>) {
  const request = memoryPreferencePlanRequestSchema.parse(input);
  if (request.privateModelTrainingEnabled && !request.explicitPrivateTrainingOptIn) {
    throw new Error("Private model training requires a separate explicit opt-in.");
  }
  return {
    schema: "dreamco.buddy_memory_preference_plan.v1",
    status: "local_preferences_ready",
    memoryCategories: [...new Set(request.memoryCategories)],
    retentionDays: request.retentionDays,
    personalizationEnabled: request.personalizationEnabled,
    privateModelTrainingEnabled: request.privateModelTrainingEnabled,
    adaptLanguageStyle: request.adaptLanguageStyle,
    personalityTraits: request.personalityTraits,
    professionalContextOverride: true,
    sensitiveMemoryDefault: "off",
    userControls: ["view", "correct", "export", "delete one", "delete all", "disable learning"],
    dataStoredByPlanner: false,
  } as const;
}
