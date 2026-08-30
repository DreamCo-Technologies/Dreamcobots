import { addEvidence, createEvidenceBundle, type EvidenceBundle, type EvidenceRecord } from './evidence-bundle.js';
import { toEvidenceRecord, type VerificationInput } from './verification-record.js';
export function recordVerification(bundle:EvidenceBundle,input:VerificationInput,timestamp?:string):EvidenceBundle { return addEvidence(bundle,toEvidenceRecord(input,timestamp)); }
export function recordBatch(projectId:string,inputs:VerificationInput[],timestamp=new Date().toISOString()):EvidenceBundle { return inputs.reduce((b,input)=>recordVerification(b,input,timestamp),createEvidenceBundle(projectId)); }
export function requiredGateStatus(bundle:EvidenceBundle):Record<'build'|'test'|'security'|'performance'|'review',boolean> { const kinds=['build','test','security','performance','review'] as const; return Object.fromEntries(kinds.map(k=>[k,bundle.records.some(r=>r.kind===k&&r.status==='pass')])) as Record<typeof kinds[number],boolean>; }
