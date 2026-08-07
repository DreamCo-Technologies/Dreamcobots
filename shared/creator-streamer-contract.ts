import { z } from "zod";

export const CREATOR_PLATFORMS = ["youtube","twitch","tiktok","instagram","facebook","x","kick","rumble","podcast","website","other"] as const;
export const CONTENT_TYPES = ["livestream","long_video","short_video","clip","podcast","music_video","tutorial","review","reaction","vlog","series_episode","community_post","thumbnail","photo_post"] as const;

export const originalAvatarSchema = z.object({
  avatarId: z.string().trim().min(3).max(160),
  displayName: z.string().trim().min(2).max(120),
  ownership: z.enum(["user_original_character","user_own_likeness","licensed_character"]),
  rightsConfirmed: z.literal(true),
  style: z.enum(["cartoon","anime_inspired_original","comic","3d","pixel","clay","storybook","mascot","realistic_original","custom"]),
  appearancePrompt: z.string().trim().min(10).max(3000),
  personalityProfileId: z.string().trim().max(160).nullable().default(null),
  voiceId: z.string().trim().max(160).nullable().default(null),
  wardrobeProfiles: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  recurringCharacter: z.boolean().default(true),
}).strict();

export const creatorProjectSchema = z.object({
  schema: z.literal("dreamco.creator_project.v1"),
  projectId: z.string().trim().min(3).max(160),
  title: z.string().trim().min(2).max(200),
  creatorProfileId: z.string().trim().min(3).max(160),
  platforms: z.array(z.enum(CREATOR_PLATFORMS)).min(1).max(12),
  contentTypes: z.array(z.enum(CONTENT_TYPES)).min(1).max(20),
  avatars: z.array(originalAvatarSchema).max(100).default([]),
  brandVoiceProfileId: z.string().trim().max(160).nullable().default(null),
  workflow: z.object({
    ideaResearch: z.boolean().default(true),
    script: z.boolean().default(true),
    recordingPlan: z.boolean().default(true),
    editingPlan: z.boolean().default(true),
    clipExtraction: z.boolean().default(true),
    thumbnailGeneration: z.boolean().default(true),
    metadataOptimization: z.boolean().default(true),
    publishingPlan: z.boolean().default(true),
    analyticsReview: z.boolean().default(true),
    sponsorTracking: z.boolean().default(false),
  }).strict(),
  publishPolicy: z.object({
    draftByDefault: z.boolean().default(true),
    freshApprovalBeforePublicPost: z.boolean().default(true),
    respectPlatformPolicy: z.literal(true),
    riskRadarRequired: z.literal(true),
  }).strict(),
}).strict();
