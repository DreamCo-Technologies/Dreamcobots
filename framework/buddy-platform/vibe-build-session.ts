import { classifyCreation, planCreation, type CreationRequest, type CreationPlan } from './universal-creation.js';
import { createProjectGraph, type ProjectGraph } from './project-graph.js';
export type SessionStage='intake'|'planned'|'ready_for_generation'|'blocked';
export interface VibeBuildSession { id:string; request:CreationRequest; plan:CreationPlan; graph:ProjectGraph; stage:SessionStage; approvals:string[]; }
export function startVibeBuildSession(id:string, request:CreationRequest):VibeBuildSession { const plan=planCreation(request); const graph=createProjectGraph(id,classifyCreation(request.prompt)); return {id,request,plan,graph,stage:'planned',approvals:[]}; }
export function approveStage(session:VibeBuildSession, stage:string):VibeBuildSession { if(!stage.trim()) throw new Error('Stage is required'); if(session.approvals.includes(stage)) return session; const approvals=[...session.approvals,stage]; return {...session,approvals,stage:stage==='requirements'?'ready_for_generation':session.stage}; }
export function requireGenerationApproval(session:VibeBuildSession):void { if(session.stage!=='ready_for_generation') throw new Error('Requirements approval is required before generation'); }
