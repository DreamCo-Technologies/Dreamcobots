import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

/** Persist complete verification output so CI artifacts retain actionable failures. */
export function persistVerificationLog(rootDirectory: string, expectationId: string, output: string): string {
  if (!/^[a-z0-9][a-z0-9-]{1,159}$/i.test(expectationId)) {
    throw new Error("Invalid verification expectation ID");
  }
  const logDirectory = resolve(rootDirectory, "logs");
  mkdirSync(logDirectory, { recursive: true });
  const logPath = resolve(logDirectory, `${expectationId}.log`);
  writeFileSync(logPath, output, "utf8");
  return logPath;
}
