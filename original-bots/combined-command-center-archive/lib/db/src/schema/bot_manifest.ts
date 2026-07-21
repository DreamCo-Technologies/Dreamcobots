import { z } from "zod/v4";

export const BOT_MANIFEST_VERSION = "1" as const;

export const botManifestSchema = z.object({
  manifestVersion: z.literal("1"),
  name: z.string().min(1).max(80).regex(/^[a-z0-9][a-z0-9_-]*$/, {
    message: "name must be lowercase alphanumeric with underscores or hyphens",
  }),
  displayName: z.string().min(1).max(120).optional(),
  description: z.string().min(1).max(500),
  division: z.enum([
    "DreamRealEstate",
    "DreamSalesPro",
    "DreamFinance",
    "DreamAI",
    "DreamSoft",
    "DreamGov",
    "DreamMedia",
    "DreamOps",
  ]),
  tier: z.enum(["FREE", "PRO", "ENTERPRISE"]),
  category: z.string().min(1).max(80),
  capabilities: z.array(z.string().min(1)).default([]),
  entrypoint: z.object({
    runtime: z.enum(["python", "node", "bun", "deno", "container"]),
    command: z.string().min(1),
    workdir: z.string().optional(),
  }),
  revenueModel: z
    .object({
      type: z.enum(["subscription", "usage", "one_time", "commission", "internal"]),
      targetMrr: z.number().nonnegative().optional(),
      currency: z.string().length(3).default("USD").optional(),
    })
    .optional(),
  dependencies: z.array(z.string()).default([]),
  owner: z.object({
    team: z.string().min(1),
    githubHandles: z.array(z.string().min(1)).default([]),
  }),
  status: z.enum(["draft", "active", "paused", "deprecated"]).default("draft"),
  tags: z.array(z.string()).default([]),
});

export type BotManifest = z.infer<typeof botManifestSchema>;

export function validateBotManifest(input: unknown):
  | { ok: true; manifest: BotManifest }
  | { ok: false; errors: string[] } {
  const result = botManifestSchema.safeParse(input);
  if (result.success) return { ok: true, manifest: result.data };
  return {
    ok: false,
    errors: result.error.issues.map(
      (i) => `${i.path.join(".") || "(root)"}: ${i.message}`,
    ),
  };
}
