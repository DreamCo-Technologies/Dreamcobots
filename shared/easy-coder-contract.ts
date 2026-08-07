import { z } from "zod";

export const EASY_CODER_INTENTS = [
  "build_app",
  "build_website",
  "fix_bug",
  "add_feature",
  "refactor",
  "write_tests",
  "deploy",
  "explain_code",
  "connect_api",
  "create_bot",
  "create_automation",
] as const;

export const easyCoderRequestSchema = z.object({
  ownerProfileId: z.string().trim().min(3).max(120),
  repository: z.string().trim().regex(/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/),
  baseBranch: z.string().trim().min(1).max(120),
  intent: z.enum(EASY_CODER_INTENTS),
  objective: z.string().trim().min(10).max(4000),
  constraints: z.array(z.string().trim().min(2).max(500)).max(100).default([]),
  preferredStack: z.array(z.string().trim().min(2).max(120)).max(30).default([]),
  allowNetworkResearch: z.boolean().default(false),
  runTests: z.boolean().default(true),
  createBranch: z.boolean().default(true),
  createPullRequest: z.boolean().default(true),
  pushApproved: z.boolean().default(false),
  deployRequested: z.boolean().default(false),
  deployApproved: z.boolean().default(false),
}).strict();

export const easyCoderPlanSchema = z.object({
  schema: z.literal("dreamco.easy_coder_plan.v1"),
  planId: z.string().trim().min(3).max(160),
  repository: z.string(),
  baseBranch: z.string(),
  workBranch: z.string(),
  intent: z.enum(EASY_CODER_INTENTS),
  objective: z.string(),
  plainLanguageSummary: z.string(),
  filesToInspect: z.array(z.string()).default([]),
  proposedFileChanges: z.array(z.object({
    path: z.string(),
    action: z.enum(["create", "update", "delete"]),
    reason: z.string(),
  }).strict()).default([]),
  commands: z.array(z.string()).default([]),
  tests: z.array(z.string()).default([]),
  approvalGates: z.array(z.string()).default([]),
  pushApproved: z.boolean(),
  deployApproved: z.boolean(),
}).strict();

export function createEasyCoderPlan(input: z.infer<typeof easyCoderRequestSchema>) {
  const request = easyCoderRequestSchema.parse(input);
  const slug = request.objective.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 48) || "change";
  const workBranch = `buddy/${request.intent}-${slug}`;
  const approvalGates = [
    "show the user the files Buddy plans to change",
    "show a plain-language summary of expected behavior",
    ...(request.runTests ? ["run the relevant tests and show failures"] : []),
    ...(!request.pushApproved ? ["get explicit approval before pushing code"] : []),
    ...(request.deployRequested && !request.deployApproved ? ["get explicit approval before deployment"] : []),
  ];

  return {
    schema: "dreamco.easy_coder_plan.v1",
    planId: `easy-coder-${Date.now()}`,
    repository: request.repository,
    baseBranch: request.baseBranch,
    workBranch,
    intent: request.intent,
    objective: request.objective,
    plainLanguageSummary: `Buddy will ${request.intent.replaceAll("_", " ")} in ${request.repository}, explain the changes in plain language, test them, and prepare an approved Git workflow.`,
    filesToInspect: [],
    proposedFileChanges: [],
    commands: [],
    tests: [],
    approvalGates,
    pushApproved: request.pushApproved,
    deployApproved: request.deployApproved,
  } as const;
}
