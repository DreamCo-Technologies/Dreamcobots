import assert from "node:assert/strict";
import test from "node:test";

import {
  createDataImportPlan,
  createDataPackagePlan,
  createMemoryPreferencePlan,
  createPrivacyRightsPlan,
} from "../server/data-rights-policy";
import { createTaskDiscoveryPlan } from "../server/task-discovery-policy";

test("task discovery helps unclear users without pretending every role is unregulated", () => {
  const plan = createTaskDiscoveryPlan({
    objective: "I do not know how to plan my investments",
    context: "personal",
    knownSteps: [],
    constraints: ["keep costs low"],
    preferredOutcome: "",
  });
  assert.equal(plan.status, "guided_discovery_ready");
  assert.equal(plan.role.id, "financial_education_assistant");
  assert.equal(plan.role.buddyIsLicensedProfessional, false);
  assert.equal(plan.externalActionTaken, false);
  assert.equal(plan.hardBoundaries.userCanDisableTheseBoundaries, false);
  assert.equal(plan.hardBoundaries.externalMoneyActionWithoutExactApprovalAllowed, false);
});

test("buyers can tune Buddy's working style without disabling professional boundaries", () => {
  const plan = createTaskDiscoveryPlan({
    objective: "Help me review a contract like a lawyer would",
    context: "business",
    knownSteps: [],
    constraints: [],
    preferredOutcome: "Prepare issues and questions for legal review",
    boundaryPreferences: {
      guidanceDepth: "teaching",
      riskDisclosure: "detailed",
      approvalMode: "review_every_step",
      moneyActionMode: "prepare_for_exact_approval",
      professionalSupport: "collaborate_with_professional",
      communicationStyle: "coach",
      voiceToneAdaptation: true,
    },
  });
  assert.equal(plan.role.id, "legal_information_assistant");
  assert.equal(plan.buyerPreferences.communicationStyle, "coach");
  assert.equal(plan.voiceToneAdaptation.enabled, true);
  assert.equal(plan.voiceToneAdaptation.emotionDiagnosisOrMentalHealthInference, false);
  assert.equal(plan.hardBoundaries.legalRepresentationAllowed, false);
});

test("data import accepts authorized references but never credentials", () => {
  const plan = createDataImportPlan({
    sourceName: "My project export",
    sourceUrl: "https://example.com/privacy/export",
    acquisition: "official_export",
    categories: ["preferences", "creative_work"],
    requestedScopes: [],
    retentionDays: 30,
    ownerConfirmsAuthority: true,
  });
  assert.equal(plan.dataImported, false);
  assert.equal(plan.controls.rawCredentialsAccepted, false);
  assert.throws(() => createDataImportPlan({
    sourceName: "Password list",
    acquisition: "user_upload",
    categories: ["credentials"],
    requestedScopes: [],
    retentionDays: 30,
    ownerConfirmsAuthority: true,
  }), /Credentials/);
});

test("privacy requests are tracked plans and cannot promise outside deletion", () => {
  const plan = createPrivacyRightsPlan({
    companyName: "Example Service",
    privacyRequestUrl: "https://example.com/privacy/request",
    jurisdiction: "California, United States",
    rights: ["access", "portability", "delete", "opt_out_sale_share"],
    identityVerificationMethod: "company_form",
    exactApprovalToSubmit: false,
  });
  assert.equal(plan.requestSubmitted, false);
  assert.equal(plan.companyComplianceGuaranteed, false);
});

test("data packages require rights and block sensitive or third-party personal data", () => {
  const base = {
    packageName: "Original synthetic workflow evaluations",
    sourceReference: "vault:owner/evaluations",
    ownershipEvidenceReference: "receipt:owner/evaluations",
    resaleRightsEvidenceReference: "rights:owner/evaluations",
    consentReceiptReference: "consent:owner/evaluations",
    provenanceReference: "provenance:owner/evaluations",
    categories: ["creative_work" as const],
    ownerCreatedData: true,
    resaleRightsConfirmed: true,
    containsMinorData: false,
    containsThirdPartyPersonalData: false,
    deidentified: true,
    recipientClass: "approved AI research organizations",
    compensationTerms: "one-year non-exclusive license",
    explicitLicenseOptIn: true,
  };
  const plan = createDataPackagePlan(base);
  assert.equal(plan.marketplaceListingCreated, false);
  assert.equal(plan.saleCompleted, false);
  assert.equal(plan.evidence.rawReferencesStored, false);
  assert.equal(plan.evidence.ownership.length, 20);
  assert.throws(() => createDataPackagePlan({ ...base, categories: ["health"] }), /Sensitive/);
  assert.throws(() => createDataPackagePlan({ ...base, categories: ["preferences"] }), /Only rights-cleared/);
  assert.throws(() => createDataPackagePlan({
    ...base,
    resaleRightsEvidenceReference: base.ownershipEvidenceReference,
  }), /distinct evidence reference/);
});

test("personality learning is selective and private training needs separate consent", () => {
  const base = {
    memoryCategories: ["preferences" as const, "learning_progress" as const],
    retentionDays: 30,
    personalizationEnabled: true,
    privateModelTrainingEnabled: false,
    explicitPrivateTrainingOptIn: false,
    adaptLanguageStyle: true,
    personalityTraits: { warmth: 0.8, directness: 0.6, patience: 0.9, curiosity: 0.8 },
  };
  const plan = createMemoryPreferencePlan(base);
  assert.equal(plan.sensitiveMemoryDefault, "off");
  assert.equal(plan.dataStoredByPlanner, false);
  assert.throws(() => createMemoryPreferencePlan({
    ...base,
    privateModelTrainingEnabled: true,
  }), /separate explicit opt-in/);
});

import assert from "node:assert/strict";
import test from "node:test";
import {
  companyDataConsentRequestSchema,
  createCompanyDataConsentPlan,
  buddyStudySourceRequestSchema,
  createBuddyStudySourcePlan,
  userSubscriptionControlRequestSchema,
  createUserSubscriptionControlPlan,
} from "../server/user-control-center-policy";

const companyBase = {
  companyOrController: "Example Platform",
  purpose: "sale" as const,
  dataCategories: ["profile" as const, "purchases" as const],
  recipientOrRecipientClass: "data marketplace partners",
  retentionDays: 180,
  jurisdiction: "United States",
  explicitUserAction: true as const,
  userAuthenticated: true as const,
  policyVersion: "1.0.0",
};

test("company sale consent is purpose-specific, explicit, and auditable", () => {
  const parsed = companyDataConsentRequestSchema.parse({ ...companyBase, decision: "opt_out", });
  const receipt = createCompanyDataConsentPlan(parsed);
  assert.equal(receipt.purpose, "sale");
  assert.equal(receipt.decision, "opt_out");
  assert.equal(receipt.effectiveInsideDreamCo, true);
  assert.equal(receipt.externalProviderAction, "not_submitted");
});

test("consent cannot be bundled or submitted without explicit authenticated action", () => {
  assert.equal(companyDataConsentRequestSchema.safeParse({ ...companyBase, decision: "opt_in", explicitUserAction: false }).success, false);
  assert.equal(companyDataConsentRequestSchema.safeParse({ ...companyBase, decision: "opt_in", userAuthenticated: false }).success, false);
});

test("Buddy can study authorized sources in read-only mode, not bypass access controls", () => {
  const input = buddyStudySourceRequestSchema.parse({
    sourceName: "My GitHub project",
    sourceType: "github_repository",
    sourceUrl: "https://github.com/example/project",
    sourceReference: "github:example/project",
    ownerAuthorized: true,
    rightsConfirmed: true,
    requestedScopes: ["contents:read", "issues:read"],
    studyPurposes: ["retrieval", "summarize", "evaluation"],
    trainingOptIn: false,
    noAccessControlBypass: true,
    noRawCredentials: true,
  });
  const plan = createBuddyStudySourcePlan(input);
  assert.equal(plan.accessMode, "read_only");
  assert.equal(plan.trainingOptIn, false);
  assert.equal(plan.dataRead, false);
  assert.equal(plan.userCanRevoke, true);
});

test("Buddy source import rejects unapproved ownership and credential collection", () => {
  const result = buddyStudySourceRequestSchema.safeParse({
    sourceName: "Private mailbox",
    sourceType: "email",
    sourceUrl: "https://mail.example.com",
    sourceReference: "mailbox:primary",
    ownerAuthorized: false,
    rightsConfirmed: true,
    requestedScopes: ["mail.read"],
    studyPurposes: ["summarize"],
    noAccessControlBypass: true,
    noRawCredentials: true,
  });
  assert.equal(result.success, false);
});

test("subscription changes require exact user approval and never claim provider execution", () => {
  const base = {
    provider: "DreamCo",
    subscriptionReference: "sub_owner_123",
    accountOwnerId: "account-owner-1",
    price: 19.99,
    currency: "USD",
    billingInterval: "monthly" as const,
    nextRenewalAt: "2026-12-01T00:00:00.000Z",
    authenticatedOwner: true as const,
  };
  assert.equal(userSubscriptionControlRequestSchema.safeParse({ ...base, action: "cancel" }).success, false);
  const input = userSubscriptionControlRequestSchema.parse({ ...base, action: "cancel", exactUserApproval: true });
  const plan = createUserSubscriptionControlPlan(input);
  assert.equal(plan.status, "awaiting_provider_execution");
  assert.equal(plan.completed, false);
  assert.equal(plan.noPaymentOrCancellationExecuted, true);
});
