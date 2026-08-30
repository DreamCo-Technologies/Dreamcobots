export type Subject = 'math' | 'science' | 'history' | 'civics' | 'business' | 'computer-science' | 'ai' | 'cybersecurity' | 'engineering' | 'career' | 'custom';
export type GameMode = 'single-player' | 'multiplayer' | 'classroom';
export type PipelineStage = 'plan' | 'generate' | 'test' | 'review' | 'pr' | 'ci' | 'deploy' | 'iterate';

export interface LearningObjective { id: string; title: string; subject: Subject; gradeBand: string; measurableOutcome: string; }
export interface CourseSpec { id: string; title: string; objectives: LearningObjective[]; lessons: string[]; assessments: string[]; }
export interface GameSpec {
  id: string; title: string; premise: string; objectives: LearningObjective[]; mode: GameMode;
  mechanics: string[]; world: { streaming: boolean; persistent: boolean; procedural: boolean; historicalContext?: string };
  systems: string[]; assessments: string[]; accessibility: string[];
}
export interface TeacherRequest { prompt: string; gradeBand: string; subject: Subject; mode?: GameMode; }
export interface AssessmentEvidence { objectiveId: string; score: number; evidence: string; attempt: number; }
export interface ModelProfile { id: string; role: string; strengths: string[]; benchmarkIds: string[]; reliability: number; }
export interface TrustFinding { category: string; severity: 'info'|'low'|'medium'|'high'|'critical'; passed: boolean; evidence: string; mitigation?: string; }
export interface TrustReport { modelId: string; benchmarkVersion: string; findings: TrustFinding[]; score: number; }
export interface SecurityScope { target: string; owner: string; authorizationId: string; allowedTechniques: string[]; expiresAt: string; }
export interface SecurityAssessment { id: string; scope: SecurityScope; status: 'authorized'|'running'|'blocked'|'complete'; findings: string[]; }
export interface BenchmarkLevel { level: number; name: string; requiredCapabilities: string[]; metrics: string[]; }
export interface PipelineState { stage: PipelineStage; approved: boolean; evidence: string[]; blockedReason?: string; }
