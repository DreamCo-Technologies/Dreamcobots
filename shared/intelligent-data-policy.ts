export type DreamCoDataClass =
  | "public"
  | "internal"
  | "user_private"
  | "sensitive_personal"
  | "financial"
  | "credential_secret"
  | "regulated_or_high_impact"
  | "generated_derived";

export type RetentionClass =
  | "ephemeral"
  | "cache"
  | "project"
  | "user_memory"
  | "business_record"
  | "security_audit"
  | "secret";

export interface IntelligentDataRecordInput {
  ownerId: string;
  purpose: string;
  source: string;
  dataClass: DreamCoDataClass;
  retentionClass: RetentionClass;
  containsRawPaymentCard?: boolean;
  containsCredential?: boolean;
  inheritedClasses?: DreamCoDataClass[];
}

const sensitivity: DreamCoDataClass[] = [
  "public",
  "internal",
  "generated_derived",
  "user_private",
  "sensitive_personal",
  "financial",
  "regulated_or_high_impact",
  "credential_secret",
];

export function highestSensitivity(classes: DreamCoDataClass[]): DreamCoDataClass {
  return classes.reduce((highest, current) =>
    sensitivity.indexOf(current) > sensitivity.indexOf(highest) ? current : highest,
  "public" as DreamCoDataClass);
}

export function validateIntelligentStorage(input: IntelligentDataRecordInput) {
  if (!input.ownerId.trim()) throw new Error("ownerId is required");
  if (!input.purpose.trim()) throw new Error("purpose is required");
  if (!input.source.trim()) throw new Error("source is required");
  if (input.containsRawPaymentCard) throw new Error("raw payment card data must never be stored by DreamCo");
  if (input.containsCredential && input.dataClass !== "credential_secret") {
    throw new Error("credentials must be classified as credential_secret");
  }
  const effectiveClass = highestSensitivity([input.dataClass, ...(input.inheritedClasses ?? [])]);
  if (effectiveClass === "credential_secret" && input.retentionClass !== "secret") {
    throw new Error("credential_secret data must use secret retention");
  }
  return {
    allowed: true,
    effectiveClass,
    storageTier:
      effectiveClass === "credential_secret" ? "secret_manager_only" :
      ["financial", "sensitive_personal", "regulated_or_high_impact", "user_private"].includes(effectiveClass) ? "user_owned_encrypted_vault" :
      effectiveClass === "public" ? "portable_catalog_or_cache" : "encrypted_local_workspace",
    requiresAccessAudit: ["financial", "sensitive_personal", "regulated_or_high_impact", "credential_secret"].includes(effectiveClass),
  };
}
