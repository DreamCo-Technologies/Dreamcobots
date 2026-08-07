import { z } from "zod";

export const BACKGROUND_POWER_MODES = ["eco","balanced","performance","maximum"] as const;

export const backgroundPerformancePermissionSchema = z.object({
  schema: z.literal("dreamco.background_performance_permission.v1"),
  ownerOrTenantId: z.string().trim().min(3).max(160),
  deviceId: z.string().trim().min(3).max(160),
  enabled: z.boolean().default(false),
  powerMode: z.enum(BACKGROUND_POWER_MODES).default("balanced"),
  allowScreenOffWork: z.boolean().default(false),
  allowBatteryDrain: z.boolean().default(false),
  allowCellularData: z.boolean().default(false),
  allowLargeDownloads: z.boolean().default(false),
  allowBackgroundUploads: z.boolean().default(false),
  allowWakeLocksWhereSupported: z.boolean().default(false),
  preferRemoteWorkersWhenOsSuspendsApp: z.boolean().default(true),
  minimumBatteryPercent: z.number().int().min(0).max(100).default(20),
  stopOnThermalState: z.enum(["fair","serious","critical"]).default("serious"),
  maximumContinuousMinutes: z.number().int().min(1).max(1440).default(120),
  freshApprovalRequiredToEnableMaximumMode: z.boolean().default(true),
  visiblePersistentStatus: z.boolean().default(true),
  userCanStopImmediately: z.literal(true),
}).strict();

export const backgroundRuntimeDecisionSchema = z.object({
  permission: backgroundPerformancePermissionSchema,
  screenOn: z.boolean(),
  batteryPercent: z.number().min(0).max(100).nullable().default(null),
  charging: z.boolean().default(false),
  thermalState: z.enum(["nominal","fair","serious","critical","unknown"]).default("unknown"),
  osBackgroundExecutionAvailable: z.boolean().default(false),
  remoteWorkerAvailable: z.boolean().default(false),
}).strict();

export function evaluateBackgroundExecution(input: z.infer<typeof backgroundRuntimeDecisionSchema>) {
  const p = input.permission;
  if (!p.enabled) return { allowed: false, mode: "stopped", reason: "background_mode_disabled" } as const;
  if (!input.screenOn && !p.allowScreenOffWork) return { allowed: false, mode: "paused", reason: "screen_off_not_authorized" } as const;
  if (input.batteryPercent !== null && !input.charging && input.batteryPercent < p.minimumBatteryPercent) {
    return { allowed: false, mode: "paused", reason: "battery_floor_reached" } as const;
  }
  if (input.thermalState === "critical" || (p.stopOnThermalState === "serious" && input.thermalState === "serious")) {
    return { allowed: false, mode: "paused", reason: "thermal_limit" } as const;
  }
  if (input.osBackgroundExecutionAvailable) {
    return { allowed: true, mode: "local_background", reason: "os_background_execution_available", powerMode: p.powerMode } as const;
  }
  if (p.preferRemoteWorkersWhenOsSuspendsApp && input.remoteWorkerAvailable) {
    return { allowed: true, mode: "remote_worker", reason: "offloaded_after_os_suspend", powerMode: p.powerMode } as const;
  }
  return { allowed: false, mode: "paused", reason: "os_background_limit" } as const;
}
