import type { PipelineStage, PipelineState } from './types.js';

const ORDER: PipelineStage[] = ['plan','generate','test','review','pr','ci','deploy','iterate'];
export function nextStage(state: PipelineState): PipelineState {
  const index = ORDER.indexOf(state.stage);
  if (index < 0) throw new Error(`Unknown stage: ${state.stage}`);
  if (!state.approved) return { ...state, blockedReason: 'Approval/evidence gate has not passed' };
  if (index === ORDER.length - 1) return state;
  return { stage: ORDER[index + 1], approved: false, evidence: [...state.evidence] };
}
export function requireEvidence(state: PipelineState, evidence: string[]): PipelineState {
  if (!evidence.length) return { ...state, approved: false, blockedReason: 'Evidence is required' };
  return { ...state, approved: true, evidence: [...new Set([...state.evidence, ...evidence])], blockedReason: undefined };
}
