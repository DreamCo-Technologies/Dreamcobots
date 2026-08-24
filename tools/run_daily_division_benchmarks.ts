import { buildBuddySuccessProgram } from "./generate_buddy_success_program";

type Check = {
  division: string;
  capabilityId: string;
  passed: boolean;
  failures: string[];
};

async function runPool<T, R>(items: T[], concurrency: number, worker: (item: T) => Promise<R>) {
  const results: R[] = new Array(items.length);
  let cursor = 0;
  async function next() {
    while (cursor < items.length) {
      const index = cursor++;
      results[index] = await worker(items[index]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, () => next()));
  return results;
}

export async function runDailyDivisionContractBenchmarks({ concurrency = 16 } = {}) {
  if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 32) {
    throw new Error("Daily division benchmark concurrency must be an integer from 1 to 32.");
  }
  const program = buildBuddySuccessProgram();
  const templates = program.improvement_templates.division_capabilities;
  const checks = program.divisions.flatMap((division) => templates.map((template) => ({ division, template })));
  const results = await runPool(checks, concurrency, async ({ division, template }): Promise<Check> => {
    const focus = division.capabilities.focuses[template.focus_index];
    const title = template.title.replace("{focus}", focus);
    const description = template.description.replace("{focus}", focus);
    const failures = [
      !focus ? "missing division focus" : "",
      /\{[^}]+\}/.test(`${title} ${description}`) ? "unresolved template token" : "",
      template.evidence_required.length < 5 ? "insufficient evidence contract" : "",
      division.production_readiness.gates.length !== 12 ? "incomplete production gate set" : "",
      division.benchmark_system.dimensions.length < 10 ? "incomplete benchmark dimensions" : "",
      division.benchmark_system.daily_operations.logical_parallel_worker_slots !== 8 ? "invalid worker slot contract" : "",
    ].filter(Boolean);
    return {
      division: division.name,
      capabilityId: `${division.capabilities.id_prefix}-${template.id}`,
      passed: failures.length === 0,
      failures,
    };
  });
  const failed = results.filter((result) => !result.passed);
  const divisionResults = program.divisions.map((division) => {
    const checksForDivision = results.filter((result) => result.division === division.name);
    const passedForDivision = checksForDivision.filter((result) => result.passed).length;
    const score = checksForDivision.length ? (passedForDivision / checksForDivision.length) * 100 : 0;
    return {
      division: division.name,
      passed: passedForDivision,
      total: checksForDivision.length,
      score,
      status: score === 100 ? "pass" : "needs_remediation",
      failures: checksForDivision.filter((result) => !result.passed).slice(0, 25),
    };
  });
  return {
    schema: "dreamco.daily_division_contract_benchmark.v2",
    divisions: program.divisions.length,
    capabilitiesChecked: results.length,
    logicalParallelWorkerSlots: program.daily_benchmark_operations.logical_parallel_worker_slots,
    runtimeConcurrency: concurrency,
    passed: results.length - failed.length,
    failed: failed.length,
    failures: failed.slice(0, 100),
    divisionResults,
    externalCompetitorRunsCompleted: 0,
    networkUsed: false,
    paidServicesUsed: false,
    productionReleasePerformed: false,
  } as const;
}

if (process.argv[1]?.endsWith("run_daily_division_benchmarks.ts")) {
  const concurrencyFlag = process.argv.find((argument) => argument.startsWith("--concurrency="));
  const concurrency = concurrencyFlag ? Number(concurrencyFlag.split("=")[1]) : 16;
  const result = await runDailyDivisionContractBenchmarks({ concurrency });
  console.log(JSON.stringify(result, null, 2));
  if (result.failed) process.exitCode = 1;
}
