import { PlannedSection } from "@/components/planned-section";
import { Brain } from "lucide-react";

export default function AILeadersPage() {
  return (
    <PlannedSection
      title="AI_Leaders"
      icon={<Brain className="h-8 w-8" />}
      status="planned"
      tagline="Top AI models by live benchmark"
      scope="~3 hours"
      willDo={[
        "Fetch a current leaderboard of frontier models (reasoning, coding, vision)",
        "Show each model's strengths, context window, and price per million tokens",
        "Highlight which models Buddy + the bot fleet currently use",
        "Refresh on a schedule so the rankings stay current",
      ]}
    />
  );
}
