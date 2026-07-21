import { PlannedSection } from "@/components/planned-section";
import { Landmark } from "lucide-react";

export default function LoansPage() {
  return (
    <PlannedSection
      title="Loans_&_Deals"
      icon={<Landmark className="h-8 w-8" />}
      status="planned"
      tagline="Financing + capital opportunities"
      scope="~4 hours"
      willDo={[
        "Aggregate loan, grant, and credit-line opportunities relevant to the empire",
        "Score each by APR, term, and fit using a transparent formula",
        "Track applications and outstanding balances against revenue",
        "Alert when a deal's terms beat the current cost of capital",
      ]}
    />
  );
}
