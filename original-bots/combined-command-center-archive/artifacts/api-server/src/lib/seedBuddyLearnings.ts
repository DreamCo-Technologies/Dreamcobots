import { db, botLearningsTable } from "@workspace/db";
import { and, eq } from "drizzle-orm";
import { logger } from "./logger";

/**
 * Puts Buddy (buddy_bot) on a learning path for the voice/image cloning,
 * consent, and legal-acknowledgment skills so they surface on the
 * learning-matrix and Buddy is explicitly tracked as acquiring them. Idempotent:
 * each skill is keyed by metadata.skill and only inserted once.
 */
const BUDDY_SKILLS: Array<{ skill: string; prompt: string; outcome: string }> = [
  {
    skill: "legal-acknowledgment-gate",
    prompt: "Guide a user to read and accept the biometric/likeness policy (BIPA, GDPR Art.9, CCPA/CPRA, EU AI Act, ELVIS Act) before any cloning.",
    outcome: "in_progress",
  },
  {
    skill: "biometric-enrollment",
    prompt: "Help a user enroll their OWN voice/image as a consented reference sample ('sign in with your voice/image to use it').",
    outcome: "in_progress",
  },
  {
    skill: "voice-cloning",
    prompt: "Produce a high-quality voice clone via the self-hosted DreamCo Voice Pro engine, gated on consent + enrollment + laws.",
    outcome: "in_progress",
  },
  {
    skill: "image-likeness-cloning",
    prompt: "Produce a high-quality likeness/image clone via the self-hosted DreamCo Likeness engine, gated on consent + enrollment + laws.",
    outcome: "in_progress",
  },
  {
    skill: "synthetic-media-disclosure",
    prompt: "Ensure cloned output is disclosed as AI-generated where the law requires, and remind users this is not legal advice.",
    outcome: "in_progress",
  },
];

export async function seedBuddyLearnings(): Promise<void> {
  try {
    for (const s of BUDDY_SKILLS) {
      const existing = await db
        .select({ id: botLearningsTable.id })
        .from(botLearningsTable)
        .where(and(eq(botLearningsTable.botSlug, "buddy_bot"), eq(botLearningsTable.kind, `skill:${s.skill}`)))
        .limit(1);
      if (existing.length > 0) continue;
      await db.insert(botLearningsTable).values({
        botSlug: "buddy_bot",
        kind: `skill:${s.skill}`,
        prompt: s.prompt,
        outcome: s.outcome,
        reward: 0,
        metadata: { skill: s.skill, domain: "cloning-consent", path: "learning" },
      });
    }
    logger.info("Buddy cloning/consent learning path seeded");
  } catch (err) {
    logger.error({ err }, "failed to seed Buddy learnings");
  }
}
