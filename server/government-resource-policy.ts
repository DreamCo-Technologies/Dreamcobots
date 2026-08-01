import { z } from "zod";

export const GOVERNMENT_RESOURCES = [
  { id: "usa_services", label: "USA.gov services", category: "general", jurisdiction: "US federal", url: "https://www.usa.gov/" },
  { id: "sam_opportunities", label: "SAM.gov contract opportunities", category: "contracts", jurisdiction: "US federal", url: "https://sam.gov/opportunities" },
  { id: "grants", label: "Grants.gov", category: "grants", jurisdiction: "US federal", url: "https://www.grants.gov/search-grants" },
  { id: "simpler_grants", label: "Simpler.Grants.gov API", category: "grants", jurisdiction: "US federal", url: "https://simpler.grants.gov/developers" },
  { id: "sba", label: "U.S. Small Business Administration", category: "business", jurisdiction: "US federal", url: "https://www.sba.gov/" },
  { id: "benefits", label: "USA.gov benefits", category: "benefits", jurisdiction: "US federal", url: "https://www.usa.gov/benefits" },
  { id: "jobs", label: "USAJOBS", category: "jobs", jurisdiction: "US federal", url: "https://www.usajobs.gov/" },
  { id: "regulations", label: "Regulations.gov", category: "regulations", jurisdiction: "US federal", url: "https://www.regulations.gov/" },
  { id: "spending", label: "USAspending.gov", category: "spending", jurisdiction: "US federal", url: "https://www.usaspending.gov/" },
  { id: "data", label: "Data.gov", category: "data", jurisdiction: "US federal", url: "https://data.gov/" },
] as const;

export const governmentResourcePlanRequestSchema = z.object({
  query: z.string().trim().min(3).max(500),
  category: z.enum(["general", "contracts", "grants", "business", "benefits", "jobs", "regulations", "spending", "data"]),
  jurisdiction: z.string().trim().min(2).max(100).default("US federal"),
  profileFacts: z.array(z.string().trim().min(2).max(160)).max(20).default([]),
  ownerApproval: z.literal(true),
}).strict();

export type GovernmentResourcePlanRequest = z.infer<typeof governmentResourcePlanRequestSchema>;

function isOfficialSource(url: string): boolean {
  const parsed = new URL(url);
  return parsed.protocol === "https:" && (parsed.hostname.endsWith(".gov") || parsed.hostname === "sam.gov");
}

export function createGovernmentResourcePlan(input: GovernmentResourcePlanRequest) {
  const exact = GOVERNMENT_RESOURCES.filter((source) => source.category === input.category);
  const resources = (exact.length ? exact : GOVERNMENT_RESOURCES.filter((source) => source.category === "general"))
    .filter((source) => isOfficialSource(source.url));
  const jurisdictionSupported = input.jurisdiction.toLowerCase() === "us federal";
  return {
    schema: "dreamco.buddy_government_resource_plan.v1",
    status: "research_plan",
    query: input.query,
    category: input.category,
    jurisdiction: input.jurisdiction,
    coverage: jurisdictionSupported ? "verified_source_registry" : "official_source_verification_required",
    profileFactsUsed: input.profileFacts,
    resources,
    workflow: [
      "Confirm the user's jurisdiction and goal.",
      "Search only official sources and preserve links and retrieval dates.",
      "Compare stated eligibility rules with user-provided facts without making a final determination.",
      "Build a deadline, document, and question checklist.",
      "Draft application material and flag claims that need evidence.",
      "Hand off signing, certification, identity checks, payment, and submission to the user.",
    ],
    guardrails: {
      eligibility: "screening_not_determination",
      legalAdvice: false,
      automaticSubmission: false,
      guaranteedOutcome: false,
      publicPageAcceptsSensitiveDocuments: false,
    },
    liveApplicationSubmitted: false,
  };
}
