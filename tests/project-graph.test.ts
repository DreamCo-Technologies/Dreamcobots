import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createProjectGraph, nextReadyNodes, verifyNode } from '../framework/buddy-platform/project-graph.js';

test('universal projects share a dependency graph',()=>{ const g=createProjectGraph('p1','game'); assert.equal(g.nodes.length,8); assert.deepEqual(nextReadyNodes(g).map(n=>n.kind),['requirement']); });
test('graph requires verified dependencies',()=>{ const g=createProjectGraph('p2','app'); assert.throws(()=>verifyNode(g,'p2-design')); const g2=verifyNode(g,'p2-requirement'); assert.equal(g2.nodes.find(n=>n.id==='p2-requirement')?.status,'verified'); assert.equal(nextReadyNodes(g2)[0].kind,'design'); });
