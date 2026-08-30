import type { GameSpec, TeacherRequest } from './types.js';

export function createTeacherGame(req: TeacherRequest): GameSpec {
  const mode = req.mode ?? 'classroom';
  const objective = { id: `obj-${req.subject}-1`, title: req.prompt, subject: req.subject, gradeBand: req.gradeBand, measurableOutcome: `Demonstrate mastery of: ${req.prompt}` };
  return {
    id: `game-${Date.now()}`, title: `Buddy Classroom: ${req.prompt.slice(0, 80)}`, premise: req.prompt,
    objectives: [objective], mode,
    mechanics: ['objective-driven missions', 'adaptive practice', 'construction/creation', 'evidence-based assessment'],
    world: { streaming: true, persistent: true, procedural: true },
    systems: ['NPC simulation', 'quests', 'inventory', 'economy-ready', 'save/load', 'multiplayer-ready', 'teacher controls'],
    assessments: [`Mastery evidence for objective ${objective.id}`],
    accessibility: ['keyboard navigation', 'captions-ready', 'configurable difficulty'],
  };
}
