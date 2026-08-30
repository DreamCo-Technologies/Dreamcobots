import type { AssessmentEvidence, CourseSpec, LearningObjective } from './types.js';

export function buildCourse(id: string, title: string, objectives: LearningObjective[], lessonCount = 5): CourseSpec {
  if (!objectives.length) throw new Error('At least one measurable learning objective is required');
  return {
    id, title, objectives,
    lessons: objectives.flatMap((o) => Array.from({ length: lessonCount }, (_, i) => `${o.id}: lesson ${i + 1}`)),
    assessments: objectives.map((o) => `Assessment: ${o.measurableOutcome}`),
  };
}

export function masteryByObjective(evidence: AssessmentEvidence[], threshold = 0.8): Record<string, boolean> {
  const latest = new Map<string, AssessmentEvidence>();
  for (const item of evidence) {
    if (item.score < 0 || item.score > 1) throw new Error(`Invalid score for ${item.objectiveId}`);
    const prior = latest.get(item.objectiveId);
    if (!prior || item.attempt > prior.attempt) latest.set(item.objectiveId, item);
  }
  return Object.fromEntries([...latest].map(([id, e]) => [id, e.score >= threshold]));
}
