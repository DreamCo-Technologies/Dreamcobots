import { z } from "zod";

export const TASK_STATES = ["queued","running","paused","waiting_approval","retrying","completed","failed","cancelled"] as const;

export const buddyQueuedTaskSchema = z.object({
  taskId: z.string().trim().min(3).max(160),
  ownerOrTenantId: z.string().trim().min(3).max(160),
  title: z.string().trim().min(2).max(240),
  priority: z.enum(["low","normal","high","critical"]).default("normal"),
  state: z.enum(TASK_STATES).default("queued"),
  estimatedCostUnits: z.number().min(0).default(1),
  cpuClass: z.enum(["tiny","light","medium","heavy","gpu"]).default("light"),
  ioClass: z.enum(["none","light","medium","heavy"]).default("light"),
  requiresNetwork: z.boolean().default(false),
  requiresDevice: z.boolean().default(false),
  deviceId: z.string().trim().max(160).nullable().default(null),
  freshApprovalRequired: z.boolean().default(false),
  dependsOn: z.array(z.string().trim().min(3).max(160)).max(100).default([]),
  retries: z.object({
    attempted: z.number().int().min(0).default(0),
    max: z.number().int().min(0).max(20).default(3),
    backoffSeconds: z.number().int().min(1).max(86400).default(30),
  }).strict(),
}).strict();

export const taskQueuePolicySchema = z.object({
  schema: z.literal("dreamco.task_queue_policy.v1"),
  maxQueuedTasks: z.number().int().min(1).max(1_000_000).default(100_000),
  maxConcurrentGlobal: z.number().int().min(1).max(10_000).default(100),
  maxConcurrentPerUser: z.number().int().min(1).max(500).default(10),
  maxConcurrentPerDevice: z.number().int().min(1).max(100).default(2),
  maxHeavyTasksPerDevice: z.number().int().min(0).max(20).default(1),
  uiBatchSize: z.number().int().min(10).max(1000).default(100),
  eventStreamBuffer: z.number().int().min(100).max(100_000).default(5000),
  backpressureHighWatermark: z.number().min(0.5).max(0.99).default(0.8),
  pauseHeavyWorkWhenDeviceBusy: z.boolean().default(true),
  preferRemoteWorkersForHeavyTasks: z.boolean().default(true),
  useWebWorkersForBrowserCpuTasks: z.boolean().default(true),
  persistQueueOutsideUiThread: z.boolean().default(true),
  lazyRenderTaskLists: z.boolean().default(true),
}).strict();

export const deviceLoadSnapshotSchema = z.object({
  deviceId: z.string().trim().min(3).max(160),
  cpuPercent: z.number().min(0).max(100),
  memoryPercent: z.number().min(0).max(100),
  batteryPercent: z.number().min(0).max(100).nullable().default(null),
  thermalState: z.enum(["nominal","fair","serious","critical","unknown"]).default("unknown"),
  networkQuality: z.enum(["offline","poor","fair","good","excellent","unknown"]).default("unknown"),
}).strict();

export function mayDispatchTask(
  task: z.infer<typeof buddyQueuedTaskSchema>,
  policy: z.infer<typeof taskQueuePolicySchema>,
  device: z.infer<typeof deviceLoadSnapshotSchema> | null,
  runningForUser: number,
  runningForDevice: number
) {
  if (runningForUser >= policy.maxConcurrentPerUser) return { allowed: false, reason: "user_concurrency_limit" } as const;
  if (task.requiresDevice && device) {
    if (runningForDevice >= policy.maxConcurrentPerDevice) return { allowed: false, reason: "device_concurrency_limit" } as const;
    const overloaded = device.cpuPercent >= 85 || device.memoryPercent >= 90 || device.thermalState === "serious" || device.thermalState === "critical";
    if (overloaded && policy.pauseHeavyWorkWhenDeviceBusy && ["medium","heavy","gpu"].includes(task.cpuClass)) {
      return { allowed: false, reason: "device_busy_backpressure" } as const;
    }
  }
  return { allowed: true, reason: "dispatch_allowed" } as const;
}
