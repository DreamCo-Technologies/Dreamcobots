import { z } from "zod";

export const canonicalSystemSchema = z.object({
  schema: z.literal("dreamco.canonical_system.v1"),
  canonicalId: z.string().trim().min(2).max(160),
  displayName: z.string().trim().min(2).max(200),
  kind: z.enum(["bot","system","service","workspace","engine","team","adapter","benchmark_suite"]),
  division: z.string().trim().min(2).max(160),
  userJobIds: z.array(z.string().trim().min(2).max(160)).min(1).max(200),
  capabilityIds: z.array(z.string().trim().min(2).max(160)).min(1).max(500),
  aliases: z.array(z.string().trim().min(2).max(160)).max(200).default([]),
  supersedes: z.array(z.string().trim().min(2).max(160)).max(200).default([]),
  status: z.enum(["canonical","migration_target","deprecated","blocked"]).default("canonical"),
}).strict();

export type CanonicalSystem = z.infer<typeof canonicalSystemSchema>;

function overlap(a: string[], b: string[]) {
  const bSet = new Set(b);
  return a.filter((value) => bSet.has(value)).length;
}

export function duplicateRisk(candidate: CanonicalSystem, existing: CanonicalSystem[]) {
  const normalizedNames = new Set([candidate.canonicalId, candidate.displayName.toLowerCase(), ...candidate.aliases.map(v => v.toLowerCase())]);
  return existing.map((current) => {
    const currentNames = new Set([current.canonicalId, current.displayName.toLowerCase(), ...current.aliases.map(v => v.toLowerCase())]);
    const exactIdentityCollision = [...normalizedNames].some((name) => currentNames.has(name));
    const sharedJobs = overlap(candidate.userJobIds, current.userJobIds);
    const sharedCapabilities = overlap(candidate.capabilityIds, current.capabilityIds);
    const jobOverlap = sharedJobs / Math.max(1, Math.min(candidate.userJobIds.length, current.userJobIds.length));
    const capabilityOverlap = sharedCapabilities / Math.max(1, Math.min(candidate.capabilityIds.length, current.capabilityIds.length));
    const score = exactIdentityCollision ? 1 : Math.min(1, jobOverlap * 0.65 + capabilityOverlap * 0.35);
    return {
      canonicalId: current.canonicalId,
      duplicateRiskScore: Number(score.toFixed(3)),
      recommendedAction: score >= 0.8 ? "extend_existing" : score >= 0.6 ? "review_for_merge_or_specialization" : "new_system_may_be_distinct",
    } as const;
  }).sort((a, b) => b.duplicateRiskScore - a.duplicateRiskScore);
}

export function mayCreateNewCanonicalSystem(candidate: CanonicalSystem, existing: CanonicalSystem[]) {
  const top = duplicateRisk(candidate, existing)[0];
  if (top && top.duplicateRiskScore >= 0.8) {
    return { allowed: false, reason: "duplicate_or_near_duplicate", existingCanonicalId: top.canonicalId, action: "extend_existing" } as const;
  }
  return { allowed: true, reason: "no_high_confidence_duplicate" } as const;
}
