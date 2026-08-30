import { startVibeBuildSession, approveStage, requireGenerationApproval, type VibeBuildSession } from './vibe-build-session.js';
import { createGenerationPlan, type GenerationPlan } from './generation-plan.js';
import { createArtifactManifest, type ArtifactManifest } from './generation-artifacts.js';
import { GovernedSandboxExecutor, type SandboxResult } from './sandbox-execution.js';
export interface BuildState { session:VibeBuildSession; generation:GenerationPlan; artifacts:ArtifactManifest; sandbox?:SandboxResult; }
export function prepareBuild(id:string,prompt:string):BuildState { const session=startVibeBuildSession(id,{prompt,inputMode:'text'}); const generation=createGenerationPlan(session); const artifacts=createArtifactManifest(id,session.plan.kind,generation); return {session,generation,artifacts}; }
export function approveRequirements(state:BuildState):BuildState { const session=approveStage(state.session,'requirements'); requireGenerationApproval(session); return {...state,session}; }
export async function verifyInSandbox(state:BuildState,command:string[]):Promise<BuildState> { requireGenerationApproval(state.session); const job={id:`${state.session.id}-sandbox`,projectId:state.session.id,command,policy:{permissions:['filesystem:workspace','network:none','process:none','secrets:none','production:none'] as const,timeoutMs:120000,maxOutputBytes:1000000}}; const sandbox=await new GovernedSandboxExecutor().run(job); return {...state,sandbox}; }
