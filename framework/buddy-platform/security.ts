import type { SecurityAssessment, SecurityScope } from './types.js';

export function authorizeSecurityAssessment(scope: SecurityScope, now = new Date()): SecurityAssessment {
  if (!scope.target || !scope.owner || !scope.authorizationId) throw new Error('Explicit target ownership and authorization are required');
  const expiry = new Date(scope.expiresAt);
  if (!Number.isFinite(expiry.getTime()) || expiry <= now) return { id: `sec-${Date.now()}`, scope, status: 'blocked', findings: ['Authorization is missing or expired'] };
  return { id: `sec-${Date.now()}`, scope, status: 'authorized', findings: [] };
}

export function canUseTechnique(assessment: SecurityAssessment, technique: string): boolean {
  return assessment.status === 'authorized' && assessment.scope.allowedTechniques.includes(technique);
}
