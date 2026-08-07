import { z } from "zod";

export const PERSONALITY_SLIDERS = [
  "warmth","humor","energy","directness","patience","formality","slang","curiosity","optimism","playfulness",
  "empathy","assertiveness","calmness","enthusiasm","creativity","skepticism","detail","brevity","coach_mode","friend_mode",
  "storytelling","challenge_level","reassurance","celebration","initiative","question_asking","proactivity","technical_depth","business_focus","learning_focus",
  "social_energy","emotional_expressiveness","structure","spontaneity","conscientiousness","openness","agreeableness","confidence","gentleness","wittiness",
  "sarcasm","motivational_intensity","accountability","reflectiveness","solution_focus","brainstorming","risk_caution","future_focus","tradition_preference","adaptability"
] as const;

export const personalitySliderSchema = z.object({
  trait: z.enum(PERSONALITY_SLIDERS),
  level: z.number().int().min(0).max(100),
}).strict();

export const buddyPersonalityProfileSchema = z.object({
  schema: z.literal("dreamco.buddy_personality.v1"),
  profileId: z.string().trim().min(3).max(120),
  displayName: z.string().trim().min(2).max(120).default("Buddy"),
  wakePhrase: z.string().trim().min(2).max(80).default("Hey Buddy"),
  archetypeId: z.string().trim().min(2).max(120),
  sliders: z.array(personalitySliderSchema).min(1).max(PERSONALITY_SLIDERS.length),
  mirrorUserStyle: z.object({
    enabled: z.boolean().default(false),
    strength: z.number().int().min(0).max(100).default(40),
    adaptVocabulary: z.boolean().default(true),
    adaptPacing: z.boolean().default(true),
    adaptHumor: z.boolean().default(true),
    adaptFormality: z.boolean().default(true),
    neverImpersonateRealPerson: z.literal(true),
  }).strict(),
  relationshipStyle: z.enum(["best_friend","coach","coworker","mentor","assistant","teammate","concierge","teacher","creative_partner","business_partner"]),
  communication: z.object({
    preferredTerms: z.array(z.string().trim().min(1).max(40)).max(100).default([]),
    avoidTerms: z.array(z.string().trim().min(1).max(40)).max(100).default([]),
    emojiLevel: z.number().int().min(0).max(100).default(20),
    voiceId: z.string().trim().max(160).nullable().default(null),
  }).strict(),
}).strict();

export const devicePersonaSchema = z.object({
  deviceId: z.string().trim().min(3).max(160),
  nickname: z.string().trim().min(2).max(80),
  personalityProfileId: z.string().trim().min(3).max(120),
  voiceId: z.string().trim().max(160).nullable().default(null),
  checkInPhrase: z.string().trim().min(2).max(240),
  role: z.enum(["phone","desktop","laptop","tablet","tv","speaker","car","wearable","home_device","other"]),
}).strict();

export const buddyDeviceRollCallSchema = z.object({
  schema: z.literal("dreamco.device_roll_call.v1"),
  wakePhrase: z.string().trim().min(2).max(80).default("Hey Buddy"),
  ownerProfileId: z.string().trim().min(3).max(120),
  devices: z.array(devicePersonaSchema).max(500),
  requireOwnerEnrollment: z.literal(true),
  announceOnlyOnlineDevices: z.boolean().default(true),
  includeCapabilitiesInCheckIn: z.boolean().default(true),
}).strict();
