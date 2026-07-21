import { PlannedSection } from "@/components/planned-section";
import { BarChart3 } from "lucide-react";

export default function DealsPage() {
  return (
    <PlannedSection
      title="Deal_Analyzer"
      icon={<BarChart3 className="h-8 w-8" />}
      status="planned"
      tagline="Real estate + business deal scoring"
      scope="~4 hours"
      willDo={[
        "Pull deal candidates from the real_estate_bot and business bots in the indexed fleet",
        "Score each deal on cap rate, cash-on-cash, and risk using a transparent formula",
        "Rank deals and flag the top opportunities with a one-click 'analyze' button per deal",
        "Persist analyses so Buddy can answer 'what's the best deal right now?'",
      ]}
    />
  );
}
