import fs from "node:fs";
import path from "node:path";

export type LiveRevenueState =
  | "sandbox_only"
  | "tests_in_progress"
  | "eligible_pending_owner"
  | "live_enabled"
  | "suspended";

type ReadinessBot = {
  slug: string;
  state: LiveRevenueState;
  live_checkout_allowed: boolean;
  blockers?: string[];
};

type ReadinessRegistry = {
  schema: string;
  bots: ReadinessBot[];
};

function readinessPath() {
  return path.resolve(process.cwd(), "config", "generated", "live-revenue-readiness.json");
}

export function loadLiveRevenueReadiness(): ReadinessRegistry {
  const file = readinessPath();
  if (!fs.existsSync(file)) {
    return { schema: "dreamco.live_revenue_readiness.generated.v1", bots: [] };
  }
  return JSON.parse(fs.readFileSync(file, "utf8")) as ReadinessRegistry;
}

export function getBotLiveRevenueState(botSlug: string): ReadinessBot {
  const registry = loadLiveRevenueReadiness();
  const row = registry.bots.find((bot) => bot.slug === botSlug);
  if (!row) {
    return {
      slug: botSlug,
      state: "sandbox_only",
      live_checkout_allowed: false,
      blockers: ["bot missing from live-revenue readiness registry"],
    };
  }
  return row;
}

export function assertBotLiveCheckoutAllowed(botSlug: string) {
  const row = getBotLiveRevenueState(botSlug);
  if (row.state !== "live_enabled" || row.live_checkout_allowed !== true) {
    const blockers = row.blockers?.length ? ` Blockers: ${row.blockers.join(", ")}` : "";
    throw new Error(`Live Stripe checkout is not enabled for ${botSlug}.${blockers}`);
  }
  return row;
}
