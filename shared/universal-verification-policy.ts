export type UniversalVerificationMode = "quick" | "ci" | "full" | "production";

export function isVerificationRunSuccessful(input: {
  mode: UniversalVerificationMode;
  failed: number;
  blocked: number;
  mergeReady: boolean;
  productionReady: boolean;
}) {
  if (input.mode === "quick") {
    return input.failed === 0 && input.blocked === 0;
  }
  if (input.mode === "full" || input.mode === "production") {
    return input.productionReady;
  }
  return input.mergeReady;
}
