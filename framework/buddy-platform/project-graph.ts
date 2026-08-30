import type { CreationKind } from './universal-creation.js';
export type GraphNodeKind = 'requirement'|'design'|'source'|'asset'|'test'|'learning'|'version'|'deployment';
export interface ProjectNode { id:string; kind:GraphNodeKind; label:string; dependsOn:string[]; status:'planned'|'ready'|'verified'|'blocked'; }
export interface ProjectGraph { projectId:string; creationKind:CreationKind; nodes:ProjectNode[]; }
const KINDS:GraphNodeKind[]=['requirement','design','source','asset','test','learning','version','deployment'];
export function createProjectGraph(projectId:string, creationKind:CreationKind):ProjectGraph { const nodes=KINDS.map((kind,i)=>({id:`${projectId}-${kind}`,kind,label:kind,dependsOn:i?[`${projectId}-${KINDS[i-1]}`]:[],status:'planned' as const})); return {projectId,creationKind,nodes}; }
export function verifyNode(graph:ProjectGraph,nodeId:string):ProjectGraph { const node=graph.nodes.find(n=>n.id===nodeId); if(!node) throw new Error(`Unknown project node: ${nodeId}`); const deps=graph.nodes.filter(n=>node.dependsOn.includes(n.id)); if(deps.some(n=>n.status!=='verified')) throw new Error('Dependencies must be verified first'); return {...graph,nodes:graph.nodes.map(n=>n.id===nodeId?{...n,status:'verified'}:n)}; }
export function nextReadyNodes(graph:ProjectGraph):ProjectNode[] { return graph.nodes.filter(n=>n.status==='planned'&&n.dependsOn.every(d=>graph.nodes.find(x=>x.id===d)?.status==='verified')); }
