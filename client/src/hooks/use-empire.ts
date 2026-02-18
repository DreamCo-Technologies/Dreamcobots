import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { EmpireOverview, AutonomyMode } from "@shared/schema";

export function useEmpireOverview() {
  return useQuery<EmpireOverview>({
    queryKey: ["/api/empire/overview"],
  });
}

export function useDivisions() {
  return useQuery<{ division: string; count: number }[]>({
    queryKey: ["/api/empire/divisions"],
  });
}

export function useAutonomyMode() {
  return useQuery({
    queryKey: ["/api/empire/settings", "autonomy_mode"],
    queryFn: async () => {
      const res = await fetch("/api/empire/settings/autonomy_mode", { credentials: "include" });
      if (res.status === 404) return { mode: "guided" as AutonomyMode };
      if (!res.ok) throw new Error("Failed to fetch autonomy mode");
      const data = await res.json();
      return (data?.value as { mode: AutonomyMode }) ?? { mode: "guided" as AutonomyMode };
    },
  });
}

export function useSetAutonomyMode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (mode: AutonomyMode) => {
      const res = await fetch("/api/empire/settings/autonomy_mode", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value: { mode } }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to set autonomy mode");
      return res.json();
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/api/empire/settings"] });
      qc.invalidateQueries({ queryKey: ["/api/empire/overview"] });
    },
  });
}

export function useBotsByDivision(division: string | null) {
  return useQuery({
    queryKey: ["/api/bots/division", division],
    enabled: !!division,
    queryFn: async () => {
      const res = await fetch(`/api/bots/division/${division}`, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch bots");
      return res.json();
    },
  });
}
