import { PlannedSection } from "@/components/planned-section";
import { Store } from "lucide-react";

export default function MarketplacePage() {
  return (
    <PlannedSection
      title="Marketplace"
      icon={<Store className="h-8 w-8" />}
      status="planned"
      tagline="Sell bot output as products"
      scope="~6 hours"
      willDo={[
        "List packaged bot outputs (apps, reports, gigs) as purchasable products",
        "Wire checkout to the existing Stripe integration for one-click purchase",
        "Track which bots generated each product and attribute revenue back to them",
        "Surface best-sellers so the fleet can prioritize what actually earns",
      ]}
      needs={["STRIPE_SECRET_KEY (already requested)"]}
    />
  );
}
