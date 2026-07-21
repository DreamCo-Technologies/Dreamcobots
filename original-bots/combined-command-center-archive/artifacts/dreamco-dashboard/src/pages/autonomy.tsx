import { PlannedSection } from "@/components/planned-section";
import { Cpu } from "lucide-react";

export default function AutonomyPage() {
  return (
    <PlannedSection
      title="Autonomy"
      icon={<Cpu className="h-8 w-8" />}
      status="planned"
      tagline="Self-running fleet controls"
      scope="~6 hours"
      willDo={[
        "Set an autonomy level per bot (manual → suggest → auto-execute)",
        "Define guardrails: spend caps, approval thresholds, kill switches",
        "Show a live feed of autonomous actions taken across the fleet",
        "One master switch to pause or resume all autonomous activity instantly",
      ]}
    />
  );
}
