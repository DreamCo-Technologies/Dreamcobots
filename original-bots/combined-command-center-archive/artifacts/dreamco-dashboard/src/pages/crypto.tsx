import { PlannedSection } from "@/components/planned-section";
import { Bitcoin } from "lucide-react";

export default function CryptoPage() {
  return (
    <PlannedSection
      title="Crypto"
      icon={<Bitcoin className="h-8 w-8" />}
      status="needs_key"
      tagline="On-chain treasury + payouts"
      scope="~5 hours"
      willDo={[
        "Show live wallet balances and recent transactions for the DreamCo treasury",
        "Track stablecoin revenue alongside Stripe fiat revenue in one view",
        "Let crypto-capable bots receive payouts and report them back to revenue",
        "Price-feed conversion so all earnings roll up into the daily target",
      ]}
      needs={["A wallet/exchange API key (e.g. Coinbase or a read-only RPC endpoint)"]}
    />
  );
}
