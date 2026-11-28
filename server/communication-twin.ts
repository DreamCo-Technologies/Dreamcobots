import { z } from "zod";

export const communicationChannelSchema = z.enum(["email", "sms", "messaging", "voice"]);
export const relationshipTierSchema = z.enum(["family", "close_friend", "professional", "vip", "unknown"]);
export const autonomyModeSchema = z.enum(["draft_only", "approval_required", "allowlisted_routine"]);

export const communicationContactPermissionSchema = z.object({
  contactId: z.string().trim().min(1).max(160),
  relationship: relationshipTierSchema.default("unknown"),
  canRead: z.boolean().default(false),
  canDraft: z.boolean().default(false),
  canSend: z.boolean().default(false),
  canAutoReply: z.boolean().default(false),
  canReceiveVoiceCalls: z.boolean().default(false),
}).strict();

export const communicationTwinSettingsSchema = z.object({
  autonomyMode: autonomyModeSchema.default("draft_only"),
  sourceConsentGranted: z.boolean().default(false),
  retainRawMessages: z.literal(false).default(false),
  retainPreferenceSummaries: z.boolean().default(true),
  ownerVoiceCloneConsent: z.boolean().default(false),
  aiDisclosureEnabled: z.boolean().default(true),
  humanTakeoverEnabled: z.literal(true).default(true),
  contacts: z.array(communicationContactPermissionSchema).default([]),
}).strict().superRefine((settings, ctx) => {
  const ids = settings.contacts.map((contact) => contact.contactId);
  if (new Set(ids).size !== ids.length) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Contact permissions must have unique contact IDs.", path: ["contacts"] });
  }
  if (!settings.aiDisclosureEnabled && settings.ownerVoiceCloneConsent) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Voice-twin operation requires AI disclosure to remain enabled.", path: ["aiDisclosureEnabled"] });
  }
});

export const communicationActionRequestSchema = z.object({
  action: z.enum(["read", "draft", "send", "auto_reply", "answer_call", "synthesize_owner_voice"]),
  channel: communicationChannelSchema,
  contactId: z.string().trim().min(1).max(160),
  content: z.string().max(12000).optional(),
  explicitOwnerApproval: z.boolean().default(false),
  lowStakesRoutine: z.boolean().default(false),
  sourceConsentGranted: z.boolean().default(false),
  ownerVoiceCloneConsent: z.boolean().default(false),
  aiDisclosureDelivered: z.boolean().default(false),
}).strict();

export type CommunicationTwinSettings = z.infer<typeof communicationTwinSettingsSchema>;
export type CommunicationActionRequest = z.infer<typeof communicationActionRequestSchema>;

const HIGH_IMPACT_PATTERNS = [
  /\b(send|transfer|wire|pay)\b.{0,50}\b(money|payment|funds|cash)\b/i,
  /\b(password|passcode|one.time.code|verification code|api key|secret)\b/i,
  /\b(i agree|accept|sign|execute)\b.{0,60}\b(contract|agreement|settlement|terms)\b/i,
  /\b(diagnosis|medical advice|prescription|legal advice|lawsuit)\b/i,
];

function isHighImpact(content = ""): boolean {
  return HIGH_IMPACT_PATTERNS.some((pattern) => pattern.test(content));
}

export function assessCommunicationAction(
  rawRequest: CommunicationActionRequest,
  rawSettings: CommunicationTwinSettings,
) {
  const request = communicationActionRequestSchema.parse(rawRequest);
  const settings = communicationTwinSettingsSchema.parse(rawSettings);
  const contact = settings.contacts.find((item) => item.contactId === request.contactId);
  const deny = (reason: string) => ({ allowed: false as const, decision: "blocked" as const, reason, requiresOwnerApproval: true });
  const allow = (decision: "allowed" | "draft_only", reason: string, requiresOwnerApproval: boolean) => ({
    allowed: true as const, decision, reason, requiresOwnerApproval,
  });

  if (!settings.sourceConsentGranted || !request.sourceConsentGranted) {
    return deny("Owner-granted source consent is required for communication access.");
  }
  if (!contact) return deny("Contact is not on the owner's explicit permission list.");

  switch (request.action) {
    case "read":
      return contact.canRead
        ? allow("allowed", "Read access is explicitly granted for this contact.", false)
        : deny("Read access is not granted for this contact.");
    case "draft":
      return contact.canDraft
        ? allow("draft_only", "A draft may be prepared; sending remains a separate action.", true)
        : deny("Draft access is not granted for this contact.");
    case "send":
      if (!contact.canSend) return deny("Send permission is not granted for this contact.");
      if (isHighImpact(request.content)) return deny("High-impact or sensitive content always requires direct owner handling.");
      if (!request.explicitOwnerApproval) return deny("Every send action requires explicit owner approval.");
      return allow("allowed", "Owner-approved message may be sent through an authorized provider.", false);
    case "auto_reply":
      if (settings.autonomyMode !== "allowlisted_routine") return deny("Autonomous replies are disabled by the current autonomy mode.");
      if (!contact.canAutoReply || !contact.canSend) return deny("This contact is not allowlisted for autonomous replies.");
      if (!request.lowStakesRoutine) return deny("Only explicitly classified low-stakes routine replies may be automated.");
      if (isHighImpact(request.content)) return deny("High-impact or sensitive content cannot be auto-replied to.");
      return allow("allowed", "Routine reply is within the owner's explicit contact and action allowlist.", false);
    case "answer_call":
      if (request.channel !== "voice") return deny("Call answering is only valid on the voice channel.");
      if (!contact.canReceiveVoiceCalls) return deny("Call answering is not authorized for this contact.");
      if (!settings.humanTakeoverEnabled) return deny("Human takeover must remain available for voice operations.");
      if (!settings.aiDisclosureEnabled || !request.aiDisclosureDelivered) return deny("AI identity disclosure must be enabled and delivered before the conversation proceeds.");
      return allow("allowed", "Disclosed AI call handling is permitted with human takeover available.", false);
    case "synthesize_owner_voice":
      if (request.channel !== "voice") return deny("Voice synthesis is only valid on the voice channel.");
      if (!settings.ownerVoiceCloneConsent || !request.ownerVoiceCloneConsent) return deny("The owner's explicit voice-cloning consent is required.");
      if (!settings.aiDisclosureEnabled || !request.aiDisclosureDelivered) return deny("Synthetic voice use requires clear AI disclosure.");
      return allow("allowed", "Owner-authorized synthetic voice may be used only with AI disclosure.", false);
  }
}

export function assessCommunicationIngestion(input: {
  source: "gmail" | "outlook" | "sms_export" | "imessage_export" | "call_transcript";
  ownerAuthorized: boolean;
  sourceConsentGranted: boolean;
  contactIds: string[];
}) {
  const source = z.object({
    source: z.enum(["gmail", "outlook", "sms_export", "imessage_export", "call_transcript"]),
    ownerAuthorized: z.boolean(),
    sourceConsentGranted: z.boolean(),
    contactIds: z.array(z.string().trim().min(1).max(160)).max(500),
  }).strict().parse(input);
  if (!source.ownerAuthorized || !source.sourceConsentGranted) {
    return { allowed: false as const, status: "blocked" as const, reason: "Authorized account access and explicit source consent are both required." };
  }
  return {
    allowed: true as const,
    status: "metadata_and_minimized_content_only" as const,
    source: source.source,
    contactCount: new Set(source.contactIds).size,
    rawMessageRetention: false as const,
    trainingEligibility: "not_authorized" as const,
  };
}

export function createCommunicationAuditEvent(input: {
  action: CommunicationActionRequest["action"];
  channel: CommunicationActionRequest["channel"];
  contactId: string;
  decision: "allowed" | "blocked" | "draft_only";
  reason: string;
  occurredAt?: string;
}) {
  return z.object({
    action: z.enum(["read", "draft", "send", "auto_reply", "answer_call", "synthesize_owner_voice"]),
    channel: communicationChannelSchema,
    contactId: z.string().trim().min(1).max(160),
    decision: z.enum(["allowed", "blocked", "draft_only"]),
    reason: z.string().trim().min(1).max(500),
    occurredAt: z.string().datetime().default(() => new Date().toISOString()),
    messageContentStored: z.literal(false).default(false),
  }).strict().parse({ ...input, messageContentStored: false });
}
