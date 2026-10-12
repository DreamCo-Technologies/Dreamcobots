export type UniversalVerificationMode = "quick" | "ci" | "full" | "production";

export function isVerificationRunSuccessful(input: {
  mode: UniversalVerificationMode;
  failed: number;
  blocked: number;
  mergeReady: boolean;
  productionReady: boolean;
  softwareVerified?: boolean;
  skipped?: number;
}) {
  if (input.mode === "quick") {
    return input.failed === 0 && input.blocked === 0;
  }
  if (input.mode === "full") {
    return input.softwareVerified === true && input.mergeReady && input.failed === 0 && input.blocked === 0 && input.skipped === 0;
  }
  if (input.mode === "production") {
    return input.productionReady;
  }
  return input.mergeReady;
}
