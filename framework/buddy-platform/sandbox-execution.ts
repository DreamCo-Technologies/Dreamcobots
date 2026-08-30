import { assertSandboxPolicy, type SandboxJob } from './sandbox-policy.js';
export interface SandboxResult { jobId:string; status:'passed'|'failed'|'blocked'; exitCode:null|number; stdout:string; stderr:string; durationMs:number; evidence:string[]; }
export interface SandboxExecutor { run(job:SandboxJob):Promise<SandboxResult>; }
/** Contract boundary: actual isolation is supplied by a host runtime; this adapter never executes generated code itself. */
export class GovernedSandboxExecutor implements SandboxExecutor { async run(job:SandboxJob):Promise<SandboxResult> { assertSandboxPolicy(job); return {jobId:job.id,status:'blocked',exitCode:null,stdout:'',stderr:'No host sandbox adapter is configured',durationMs:0,evidence:['policy-validated','execution-not-attempted']}; } }
