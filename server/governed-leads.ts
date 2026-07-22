import { createHash } from "node:crypto";
import { z } from "zod";

export const LEAD_CHANNELS = ["email", "sms", "voice_call", "social_dm"] as const;
export type LeadChannel = typeof LEAD_CHANNELS[number];

const TOKEN_LIKE = /(?:github_pat_|ghs_|(?:sk|rk)_(?:live|test)_|BEGIN .*PRIVATE KEY)/i;
const safeText = (minimum: number, maximum: number) => z.string().trim().min(minimum).max(maximum).refine(
  (value) => !TOKEN_LIKE.test(value),
  "Lead workflows must not contain credentials",
);
const opaqueContactRef = z.string().regex(
  /^contact_ref:[A-Za-z0-9_-]{8,80}$/,
  "Use an opaque contact reference, never a raw email address or phone number",
);
const isoDate = z.string().datetime({ offset: true });

export const leadCandidateSchema = z.object({
  leadId: z.string().regex(/^lead-[A-Za-z0-9-]{4,80}$/),
  organizationName: safeText(2, 120),
  contactRef: opaqueContactRef,
  source: z.object({
    type: z.enum([
      "owner_supplied",
      "inbound_request",
      "existing_customer_record",
      "public_business_directory",
      "owner_authorized_provider_api",
    ]),
    reference: z.string().regex(/^[A-Za-z][A-Za-z0-9_.:/-]{2,180}$/),
    termsConfirmed: z.literal(true),
    purchasedOrStolenList: z.literal(false),
  }).strict(),
  consent: z.object({
    basis: z.enum(["explicit_opt_in", "inbound_request", "existing_relationship", "none"]),
    channels: z.array(z.enum(LEAD_CHANNELS)).max(LEAD_CHANNELS.length),
    obtainedAt: isoDate.optional(),
    expiresAt: isoDate.optional(),
    evidenceRef: z.string().regex(/^[A-Za-z][A-Za-z0-9_.:/-]{2,180}$/).optional(),
  }).strict(),
  engagement: z.object({
    state: z.enum(["never_contacted", "waiting", "replied", "unsubscribed", "bounced", "complaint"]),
    followUpsSent: z.number().int().min(0).max(3),
    sentToday: z.number().int().min(0).max(1),
    lastContactAt: isoDate.optional(),
  }).strict(),
  qualificationSignals: z.array(safeText(2, 120)).max(12).default([]),
  sensitiveTargeting: z.literal(false),
  includesMinor: z.literal(false),
}).strict().superRefine((lead, context) => {
  const uniqueChannels = new Set(lead.consent.channels);
  if (uniqueChannels.size !== lead.consent.channels.length) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["consent", "channels"], message: "Consent channels must be unique" });
  }
  if (lead.consent.basis === "none" && lead.consent.channels.length) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["consent", "channels"], message: "No-consent leads cannot have permitted channels" });
  }
  if (lead.consent.basis !== "none" && (!lead.consent.obtainedAt || !lead.consent.evidenceRef)) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["consent"], message: "Contact permission requires timestamped evidence" });
  }
  if (
    lead.consent.channels.some((channel) => channel === "sms" || channel === "voice_call") &&
    lead.consent.basis !== "explicit_opt_in"
  ) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["consent", "basis"], message: "SMS and voice calls require explicit opt-in" });
  }
  if (lead.engagement.state !== "never_contacted" && !lead.engagement.lastContactAt) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["engagement", "lastContactAt"], message: "Prior engagement requires a last-contact timestamp" });
  }
});

export const leadCampaignRequestSchema = z.object({
  campaignId: z.string().regex(/^campaign-[A-Za-z0-9-]{4,80}$/),
  ownerUserId: z.string().regex(/^[A-Za-z0-9_.:-]{2,80}$/),
  botSlug: z.string().regex(/^[a-z0-9][a-z0-9-]{1,79}$/),
  objective: safeText(10, 300),
  audience: safeText(3, 200),
  offer: safeText(3, 300),
  requestedChannels: z.array(z.enum(LEAD_CHANNELS)).min(1).max(LEAD_CHANNELS.length),
  prospects: z.array(leadCandidateSchema).min(1).max(100),
  suppressionRefs: z.array(opaqueContactRef).max(10_000).default([]),
  campaignSendsToday: z.number().int().min(0).max(50).default(0),
  maximumDailySends: z.number().int().min(1).max(50).default(20),
  minimumFollowUpHours: z.number().int().min(24).max(720).default(48),
  maximumFollowUps: z.number().int().min(0).max(3).default(2),
}).strict().superRefine((campaign, context) => {
  if (new Set(campaign.requestedChannels).size !== campaign.requestedChannels.length) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["requestedChannels"], message: "Requested channels must be unique" });
  }
  const leadIds = campaign.prospects.map((lead) => lead.leadId);
  if (new Set(leadIds).size !== leadIds.length) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["prospects"], message: "Lead ids must be unique" });
  }
});

export const leadActionApprovalSchema = z.object({
  approvalRequestId: z.string().regex(/^approval-[A-Za-z0-9-]{4,80}$/),
  actionId: z.string().regex(/^lead-action-[a-f0-9]{20}$/),
  campaignId: z.string().regex(/^campaign-[A-Za-z0-9-]{4,80}$/),
  leadId: z.string().regex(/^lead-[A-Za-z0-9-]{4,80}$/),
  ownerUserId: z.string().regex(/^[A-Za-z0-9_.:-]{2,80}$/),
  botSlug: z.string().regex(/^[a-z0-9][a-z0-9-]{1,79}$/),
  channel: z.enum(LEAD_CHANNELS),
  stepNumber: z.number().int().min(1).max(4),
  approvedAt: isoDate,
  expiresAt: isoDate,
  oneActionOnly: z.literal(true),
}).strict();

export type LeadCampaignRequest = z.infer<typeof leadCampaignRequestSchema>;
export type LeadActionApproval = z.infer<typeof leadActionApprovalSchema>;

export type LeadAction = {
  actionId: string;
  leadId: string;
  contactRef: string;
  organizationName: string;
  channel: LeadChannel | null;
  stepNumber: number;
  status: "approval_required" | "research_only" | "waiting_for_cadence" | "suppressed" | "daily_limit_reached" | "sequence_complete";
  reason: string;
  draft: string | null;
  earliestSendAt: string | null;
  externalActionTaken: false;
};

export type GovernedLeadPlan = {
  schema: "dreamco.governed_lead_plan.v1";
  campaignId: string;
  ownerUserId: string;
  botSlug: string;
  status: "approval_actions_ready" | "research_only";
  actions: LeadAction[];
  summary: {
    prospects: number;
    approvalRequired: number;
    blockedOrWaiting: number;
  };
  guardrails: {
    recipientPermissionRequired: true;
    exactOwnerApprovalPerMessage: true;
    optOutReplyBounceAndComplaintStop: true;
    purchasedOrStolenListsForbidden: true;
    privateOrTermsBypassingCollectionForbidden: true;
    sensitiveTargetingForbidden: true;
    minorsExcluded: true;
    rawContactDetailsAccepted: false;
    platformTermsMustBeConfirmed: true;
    revenueGuaranteed: false;
  };
  externalActionTaken: false;
};

const terminalStates = new Set(["replied", "unsubscribed", "bounced", "complaint"]);

function actionId(campaignId: string, leadId: string, channel: string, stepNumber: number) {
  const digest = createHash("sha256").update(`${campaignId}:${leadId}:${channel}:${stepNumber}`).digest("hex").slice(0, 20);
  return `lead-action-${digest}`;
}

function selectChannel(lead: z.infer<typeof leadCandidateSchema>, requested: LeadChannel[], now: Date) {
  if (lead.consent.basis === "none") return null;
  if (lead.consent.obtainedAt && Date.parse(lead.consent.obtainedAt) > now.getTime()) return null;
  if (lead.consent.expiresAt && Date.parse(lead.consent.expiresAt) <= now.getTime()) return null;
  return requested.find((channel) => lead.consent.channels.includes(channel)) ?? null;
}

function leadDraft(organizationName: string, offer: string, stepNumber: number) {
  if (stepNumber === 1) return `Hello ${organizationName}, you gave permission to receive information about ${offer}. Would you like the details?`;
  return `Hello ${organizationName}, this is follow-up ${stepNumber - 1} about ${offer}. Reply stop at any time and we will not contact you again.`;
}

export function buildGovernedLeadPlan(input: LeadCampaignRequest, now = new Date()): GovernedLeadPlan {
  const campaign = leadCampaignRequestSchema.parse(input);
  const suppression = new Set(campaign.suppressionRefs);
  let remainingDailySlots = Math.max(campaign.maximumDailySends - campaign.campaignSendsToday, 0);
  const actions = campaign.prospects.map<LeadAction>((lead) => {
    const stepNumber = lead.engagement.followUpsSent + 1;
    const channel = selectChannel(lead, campaign.requestedChannels, now);
    const id = actionId(campaign.campaignId, lead.leadId, channel ?? "research", stepNumber);
    const base = {
      actionId: id,
      leadId: lead.leadId,
      contactRef: lead.contactRef,
      organizationName: lead.organizationName,
      channel,
      stepNumber,
      draft: null,
      earliestSendAt: null,
      externalActionTaken: false as const,
    };
    if (suppression.has(lead.contactRef) || terminalStates.has(lead.engagement.state)) {
      return { ...base, status: "suppressed", reason: `contact_stopped:${lead.engagement.state}` };
    }
    if (!channel) {
      return { ...base, status: "research_only", reason: "documented_recipient_channel_permission_required" };
    }
    if (lead.engagement.sentToday >= 1 || remainingDailySlots <= 0) {
      return {
        ...base,
        status: "daily_limit_reached",
        reason: lead.engagement.sentToday >= 1 ? "contact_daily_cap_reached" : "campaign_daily_cap_reached",
      };
    }
    if (lead.engagement.followUpsSent > campaign.maximumFollowUps) {
      return { ...base, status: "sequence_complete", reason: "maximum_follow_ups_reached" };
    }
    if (lead.engagement.lastContactAt) {
      const earliest = new Date(Date.parse(lead.engagement.lastContactAt) + campaign.minimumFollowUpHours * 60 * 60 * 1000);
      if (earliest.getTime() > now.getTime()) {
        return { ...base, status: "waiting_for_cadence", reason: "minimum_follow_up_interval", earliestSendAt: earliest.toISOString() };
      }
    }
    remainingDailySlots -= 1;
    return {
      ...base,
      status: "approval_required",
      reason: "recipient_permission_verified_owner_approval_required",
      draft: leadDraft(lead.organizationName, campaign.offer, stepNumber),
    };
  });
  const approvalRequired = actions.filter((action) => action.status === "approval_required").length;
  return {
    schema: "dreamco.governed_lead_plan.v1",
    campaignId: campaign.campaignId,
    ownerUserId: campaign.ownerUserId,
    botSlug: campaign.botSlug,
    status: approvalRequired ? "approval_actions_ready" : "research_only",
    actions,
    summary: {
      prospects: campaign.prospects.length,
      approvalRequired,
      blockedOrWaiting: campaign.prospects.length - approvalRequired,
    },
    guardrails: {
      recipientPermissionRequired: true,
      exactOwnerApprovalPerMessage: true,
      optOutReplyBounceAndComplaintStop: true,
      purchasedOrStolenListsForbidden: true,
      privateOrTermsBypassingCollectionForbidden: true,
      sensitiveTargetingForbidden: true,
      minorsExcluded: true,
      rawContactDetailsAccepted: false,
      platformTermsMustBeConfirmed: true,
      revenueGuaranteed: false,
    },
    externalActionTaken: false,
  };
}

export function authorizeLeadAction(plan: GovernedLeadPlan, approvalInput: LeadActionApproval, now = new Date()) {
  const approval = leadActionApprovalSchema.parse(approvalInput);
  const action = plan.actions.find((candidate) => candidate.actionId === approval.actionId);
  if (!action || action.status !== "approval_required" || !action.channel || !action.draft) {
    throw new Error("Lead action is not eligible for dispatch approval");
  }
  if (
    approval.campaignId !== plan.campaignId ||
    approval.ownerUserId !== plan.ownerUserId ||
    approval.botSlug !== plan.botSlug ||
    approval.leadId !== action.leadId ||
    approval.channel !== action.channel ||
    approval.stepNumber !== action.stepNumber
  ) {
    throw new Error("Approval does not match the exact lead action");
  }
  const approvedAt = Date.parse(approval.approvedAt);
  const expiresAt = Date.parse(approval.expiresAt);
  if (approvedAt > now.getTime() || expiresAt <= now.getTime() || expiresAt - approvedAt > 86_400_000) {
    throw new Error("Approval is invalid, expired, or exceeds the 24-hour limit");
  }
  return {
    schema: "dreamco.lead_dispatch_packet.v1",
    status: "ready_for_configured_adapter",
    approvalRequestId: approval.approvalRequestId,
    actionId: action.actionId,
    campaignId: plan.campaignId,
    ownerUserId: plan.ownerUserId,
    botSlug: plan.botSlug,
    leadId: action.leadId,
    contactRef: action.contactRef,
    channel: action.channel,
    message: action.draft,
    stepNumber: action.stepNumber,
    oneActionOnly: true,
    idempotencyKey: action.actionId,
    externalDispatchExecuted: false,
  } as const;
}

export class LeadSuppressionLedger {
  private readonly entries = new Map<string, { reason: string; suppressedAt: string }>();

  constructor(private readonly maximumEntries = 10_000) {
    if (!Number.isInteger(maximumEntries) || maximumEntries < 1) {
      throw new Error("Suppression capacity must be a positive integer");
    }
  }

  suppress(contactRefInput: string, reason: "opt_out" | "reply" | "bounce" | "complaint" | "owner_block", now = new Date()) {
    const contactRef = opaqueContactRef.parse(contactRefInput);
    if (!this.entries.has(contactRef) && this.entries.size >= this.maximumEntries) {
      throw new Error("Suppression capacity reached; persist the ledger before accepting more outreach");
    }
    this.entries.set(contactRef, { reason, suppressedAt: now.toISOString() });
  }

  has(contactRefInput: string) {
    return this.entries.has(opaqueContactRef.parse(contactRefInput));
  }

  list() {
    return [...this.entries.entries()].map(([contactRef, entry]) => ({ contactRef, ...entry }));
  }
}
