import type { CreationKind } from './universal-creation.js';
import type { GenerationPlan } from './generation-plan.js';
export interface ArtifactSpec { id:string; kind:'source'|'test'|'docs'|'config'|'asset'; path:string; purpose:string; generatedBy:'buddy'; requiresEvidence:boolean; }
export interface ArtifactManifest { projectId:string; creationKind:CreationKind; artifacts:ArtifactSpec[]; }
export function createArtifactManifest(projectId:string,creationKind:CreationKind,plan:GenerationPlan):ArtifactManifest { const tasks=plan.tasks.filter(t=>t.status!=='blocked'); return {projectId,creationKind,artifacts:tasks.map(t=>({id:`${projectId}-${t.id}`,kind:t.artifact,path:`generated/${projectId}/${t.id}`,purpose:t.description,generatedBy:'buddy',requiresEvidence:t.phase==='verification'||t.artifact==='source'||t.artifact==='test'}))}; }
export function assertArtifactEvidence(manifest:ArtifactManifest,verifiedArtifactIds:string[]):void { const missing=manifest.artifacts.filter(a=>a.requiresEvidence&&!verifiedArtifactIds.includes(a.id)); if(missing.length) throw new Error(`Missing evidence for ${missing.length} artifact(s)`); }
