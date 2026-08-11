import OpenAI from "openai";
import { z } from "zod";

import { compileIntelligentTask } from "./intelligent-task-router";

export const publicBuddyExecutionRequestSchema = z.object({
  objective: z.string().trim().min(3).max(8000),
  mode: z.enum(["Build", "Fix", "Create", "Plan", "Discover"]).default("Build"),
  requestedCapabilities: z.array(z.string().trim().min(2).max(160)).max(30).default([]),
  approvePaidModelForThisRequest: z.boolean().default(false),
  preferredBotSlug: z.string().trim().min(1).max(160).optional(),
}).strict();

type PublicBuddyExecutionRequest = z.infer<typeof publicBuddyExecutionRequestSchema>;

function requiresExternalApproval(objective: string) {
  return /\b(send|email|message|post|publish|buy|purchase|pay|transfer|move money|submit|file with|sign|delete|merge|deploy production|change password|change account|contact customer|call customer)\b/i.test(objective);
}

function configuredOpenAIClient() {
  const apiKey = process.env.AI_INTEGRATIONS_OPENAI_API_KEY || process.env.OPENAI_API_KEY;
  if (!apiKey) return null;
  return new OpenAI({
    apiKey,
    baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL || undefined,
  });
}

function executionModel() {
  return process.env.BUDDY_EXECUTION_MODEL || process.env.AI_INTEGRATIONS_OPENAI_MODEL || "gpt-4.1-mini";
}

function executorSystemPrompt(mode: PublicBuddyExecutionRequest["mode"], externalApprovalRequired: boolean) {
  return [
    "You are Buddy's execution worker inside DreamCo.",
    "The user is testing whether Buddy actually completes requests instead of behaving like a generic chatbot.",
    `Task mode: ${mode}.`,
    "Produce the requested usable artifact, analysis, code, draft, answer, or repair output directly.",
    "Do not spend most of the response explaining what you could do. Do the safe in-response work now.",
    "When code is requested, provide the implementation or patch content. When writing is requested, provide the finished writing. When analysis is requested, provide conclusions and evidence needs. When planning is requested, provide the plan because the plan itself is the requested artifact.",
    externalApprovalRequired
      ? "The objective appears to include an external/consequential action. Prepare the exact action and any content needed, but do not claim it was sent, published, purchased, deployed, submitted, deleted, merged, or otherwise executed. Mark the approval boundary clearly."
      : "No external consequential action was detected. Complete all safe content-generation and reasoning work in this response.",
    "Be explicit about anything that still requires a tool, credential, external service, repository write capability, or owner approval.",
    "Never fabricate tool use or execution receipts.",
  ].join("\n");
}

export async function executePublicBuddyRequest(
  input: z.input<typeof publicBuddyExecutionRequestSchema>,
) {
  const request = publicBuddyExecutionRequestSchema.parse(input);
  const externalApprovalRequired = requiresExternalApproval(request.objective);
  const compilation = compileIntelligentTask({
    objective: request.objective,
    requiredCapabilities: request.requestedCapabilities,
    allowPaid: request.approvePaidModelForThisRequest,
    maximumParallelLanes: 32,
  });

  if (externalApprovalRequired) {
    return {
      schema: "dreamco.public_buddy_execution.v1",
      status: "prepared_for_approval",
      executed: false,
      objective: request.objective,
      compilation,
      receipt: {
        state: "prepared_for_approval",
        reason: "An external or consequential action requires a configured adapter and exact owner approval.",
      },
      output: "Buddy routed the task and identified an approval boundary. Connect the required adapter or use the authenticated execution environment to perform the outside action. No outside action was falsely claimed as completed.",
    } as const;
  }

  const client = configuredOpenAIClient();
  if (!client || !request.approvePaidModelForThisRequest) {
    return {
      schema: "dreamco.public_buddy_execution.v1",
      status: client ? "model_approval_required" : "backend_model_not_configured",
      executed: false,
      objective: request.objective,
      compilation,
      receipt: {
        state: "prepared_for_execution",
        reason: client
          ? "The backend has a model connector, but this request did not approve provider execution."
          : "The backend is reachable but no execution model credential is configured.",
      },
      output: "The request was compiled into a real DreamCo execution graph, but no model/tool execution was performed. Enable an approved execution model for this request or configure a local/open-weight execution adapter.",
    } as const;
  }

  const model = executionModel();
  const response = await client.chat.completions.create({
    model,
    messages: [
      { role: "system", content: executorSystemPrompt(request.mode, false) },
      { role: "user", content: request.objective },
    ],
    max_completion_tokens: 4000,
  });
  const output = response.choices[0]?.message?.content?.trim() || "";
  if (!output) throw new Error("Execution model returned no usable output.");

  return {
    schema: "dreamco.public_buddy_execution.v1",
    status: "executed_safe_response_work",
    executed: true,
    objective: request.objective,
    compilation,
    receipt: {
      state: "executed",
      model,
      provider: "openai-compatible-backend",
      externalActionsExecuted: false,
      generatedAt: new Date().toISOString(),
    },
    output,
  } as const;
}
