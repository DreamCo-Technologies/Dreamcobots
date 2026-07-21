import { PlannedSection } from "@/components/planned-section";
import { Rocket } from "lucide-react";

export default function BusinessPage() {
  return (
    <PlannedSection
      title="Biz_Launch"
      icon={<Rocket className="h-8 w-8" />}
      status="planned"
      tagline="Spin up new revenue lines"
      scope="~5 hours"
      willDo={[
        "Template new business ideas and assign them to Business_bots from the fleet",
        "Generate a launch checklist (landing page, pricing, first customer) per idea",
        "Track each launch from idea → live → first dollar",
        "Feed launched businesses into the revenue and cost trackers automatically",
      ]}
    />
  );
}
