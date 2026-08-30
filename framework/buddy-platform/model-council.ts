import type { ModelProfile } from './types.js';

export const COUNCIL_ROLES = ['research','coding','architecture','education','game-design','security','testing','performance','governance','curriculum','ai-safety'];
export function buildCouncil(count = 500): ModelProfile[] {
  if (count < 1) throw new Error('Council must contain at least one model');
  return Array.from({ length: count }, (_, i) => ({ id: `model-${String(i + 1).padStart(3,'0')}`, role: COUNCIL_ROLES[i % COUNCIL_ROLES.length], strengths: [], benchmarkIds: [], reliability: 0 }));
}
export function councilQuorum(total: number, approvals: number, minimumRatio = .67): boolean {
  if (total < 1 || approvals < 0 || approvals > total) return false;
  return approvals / total >= minimumRatio;
}
