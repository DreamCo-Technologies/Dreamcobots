import { z } from "zod";

export const neutralToolSchema = z.object({
  name: z.string().trim().min(1).max(128),
  description: z.string().trim().min(1).max(1000),
  inputSchema: z.record(z.string(), z.unknown()).default({ type: "object", properties: {} }),
}).strict();

export const neutralModelTaskSchema = z.object({
  objective: z.string().trim().min(3).max(20_000),
  systemInstructions: z.string().trim().max(20_000).default(""),
  context: z.string().max(200_000).default(""),
  tools: z.array(neutralToolSchema).max(64).default([]),
  requireStructuredOutput: z.boolean().default(false),
  outputSchema: z.record(z.string(), z.unknown()).optional(),
  reasoningEffort: z.enum(["low", "medium", "high"]).default("medium"),
}).strict();

export type NeutralModelTask = z.infer<typeof neutralModelTaskSchema>;

export type ProviderProtocol =
  | "openai_responses"
  | "anthropic_messages"
  | "google_generate_content"
  | "mistral_chat"
  | "openai_compatible";

function prompt(task: NeutralModelTask) {
  return task.context ? `${task.objective}\n\nContext:\n${task.context}` : task.objective;
}

function openAiTools(task: NeutralModelTask) {
  return task.tools.map((tool) => ({
    type: "function",
    name: tool.name,
    description: tool.description,
    parameters: tool.inputSchema,
  }));
}

function anthropicTools(task: NeutralModelTask) {
  return task.tools.map((tool) => ({
    name: tool.name,
    description: tool.description,
    input_schema: tool.inputSchema,
  }));
}

function googleTools(task: NeutralModelTask) {
  return task.tools.length
    ? [{
        functionDeclarations: task.tools.map((tool) => ({
          name: tool.name,
          description: tool.description,
          parametersJsonSchema: tool.inputSchema,
        })),
      }]
    : [];
}

export function compileModelTask(
  input: z.input<typeof neutralModelTaskSchema>,
  protocol: ProviderProtocol,
  exactModelId: string,
) {
  const task = neutralModelTaskSchema.parse(input);
  if (!exactModelId.trim()) throw new Error("Exact model id is required before provider execution.");

  switch (protocol) {
    case "openai_responses":
      return {
        protocol,
        request: {
          model: exactModelId,
          instructions: task.systemInstructions || undefined,
          input: prompt(task),
          tools: openAiTools(task),
          reasoning: { effort: task.reasoningEffort },
          ...(task.requireStructuredOutput && task.outputSchema
            ? { text: { format: { type: "json_schema", name: "dreamco_output", schema: task.outputSchema } } }
            : {}),
        },
        toolDialect: "openai_function_tool",
      } as const;

    case "anthropic_messages":
      return {
        protocol,
        request: {
          model: exactModelId,
          system: task.systemInstructions || undefined,
          messages: [{ role: "user", content: prompt(task) }],
          tools: anthropicTools(task),
          max_tokens: 8192,
        },
        toolDialect: "anthropic_input_schema",
      } as const;

    case "google_generate_content":
      return {
        protocol,
        request: {
          model: exactModelId,
          systemInstruction: task.systemInstructions || undefined,
          contents: [{ role: "user", parts: [{ text: prompt(task) }] }],
          tools: googleTools(task),
          generationConfig: task.requireStructuredOutput && task.outputSchema
            ? { responseMimeType: "application/json", responseJsonSchema: task.outputSchema }
            : undefined,
        },
        toolDialect: "gemini_function_declarations",
      } as const;

    case "mistral_chat":
    case "openai_compatible":
      return {
        protocol,
        request: {
          model: exactModelId,
          messages: [
            ...(task.systemInstructions ? [{ role: "system", content: task.systemInstructions }] : []),
            { role: "user", content: prompt(task) },
          ],
          tools: task.tools.map((tool) => ({
            type: "function",
            function: {
              name: tool.name,
              description: tool.description,
              parameters: tool.inputSchema,
            },
          })),
          ...(task.requireStructuredOutput ? { response_format: { type: "json_object" } } : {}),
        },
        toolDialect: "openai_compatible_function_tool",
      } as const;
  }
}

export function protocolForProvider(providerId: string): ProviderProtocol {
  if (providerId === "openai" || providerId === "xai") return "openai_responses";
  if (providerId === "anthropic") return "anthropic_messages";
  if (providerId === "google") return "google_generate_content";
  if (providerId === "mistral") return "mistral_chat";
  return "openai_compatible";
}
