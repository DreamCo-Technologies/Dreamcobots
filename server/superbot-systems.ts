import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import { Router } from 'express';
import { z } from 'zod';
import { getFleetRuntimeRegistry, type FleetRuntimeRegistry } from './fleet-runtime';

type Candidate = { slug: string; name: string; reason: string };
type Subject = {
  id: string; name: string | null; purpose: string | null; primary_owner: string;
  collaborators: string[]; source_status: string; source_refs: string[];
  capabilities: string[]; candidate_bots: Candidate[]; state: string;
};
type Crosswalk = {
  schema_version: number; source_hashes: Record<string, string>;
  summary: Record<string, number>; proposals: Subject[]; bots: Subject[]; legacy: Subject[];
};
const kinds = ['proposal', 'bot', 'legacy'] as const;
type Kind = typeof kinds[number];
export const superbotPlanSchema = z.object({
  kind: z.enum(kinds), id: z.string().min(1).max(160),
  objective: z.string().trim().min(10).max(4000),
}).strict();

export class SuperbotSystems {
  constructor(readonly crosswalk: Crosswalk, private fleet: FleetRuntimeRegistry) {
    if (crosswalk.schema_version !== 1) throw new Error('Unsupported superbot crosswalk');
    for (const rows of [crosswalk.proposals, crosswalk.bots, crosswalk.legacy]) {
      if (new Set(rows.map(row => row.id)).size !== rows.length) throw new Error('Duplicate subject ID');
    }
  }

  static fromFile(root = process.cwd(), fleet = getFleetRuntimeRegistry()) {
    const data = JSON.parse(readFileSync(resolve(root, 'config/generated/superbot-crosswalk.json'), 'utf8')) as Crosswalk;
    // Fail closed on stale source instead of silently routing an obsolete mapping.
    for (const [file, expected] of Object.entries(data.source_hashes)) {
      const path = resolve(root, file);
      if (!path.startsWith(resolve(root) + sep)) throw new Error('Crosswalk source path escaped repository');
      const actual = createHash('sha256').update(readFileSync(path)).digest('hex');
      if (actual !== expected) throw new Error(`Stale superbot crosswalk: ${file}; run python3 tools/build_superbot_crosswalk.py`);
    }
    return new SuperbotSystems(data, fleet);
  }

  rows(kind: Kind) {
    return kind === 'proposal' ? this.crosswalk.proposals : kind === 'bot' ? this.crosswalk.bots : this.crosswalk.legacy;
  }

  get(kind: Kind, id: string) { return this.rows(kind).find(row => row.id === id); }

  plan(input: unknown) {
    const request = superbotPlanSchema.parse(input);
    const subject = this.get(request.kind, request.id);
    if (!subject) return { status: 'not_found' as const, planningOnly: true, liveExternalActionTaken: false };
    const base = { subject, planningOnly: true, liveExternalActionTaken: false,
      capabilityImplementationVerified: false,
      boundary: 'These are shared sandbox planning packets, not execution of the proposed or historical capability.' };
    if (!['recovered','generated'].includes(subject.source_status)) {
      return { ...base, status: 'source_required' as const, taskPackets: [] };
    }
    const selected = subject.candidate_bots.slice(0,3).map(candidate => this.fleet.get(candidate.slug));
    if (!selected.length || selected.some(bot => !bot || bot.health().state !== 'ready')) {
      return { ...base, status: 'implementation_required' as const, taskPackets: [] };
    }
    const taskPackets = selected.map(bot => bot!.execute({
      objective: request.objective,
      input: { subjectId: subject.id, subjectKind: request.kind, primaryOwner: subject.primary_owner },
      requestedCapabilities: subject.capabilities.slice(0,20).filter(capability => capability.length >= 2 && capability.length <= 160),
      liveActionRequested: false,
    }));
    return { ...base, status: 'coordination_plan_ready' as const, taskPackets,
      acceptanceRequirements: ['Implement a bounded domain adapter with synthetic fixtures.',
        'Verify output semantics, error behavior and permissions independently.',
        'Record integration evidence separately before any live or production promotion.'] };
  }
}

export function createSuperbotRouter(load = () => SuperbotSystems.fromFile()) {
  const router = Router();
  // Load per request: source changes must not be hidden by a stale long-lived cache.
  router.use((_req, res, next) => { res.setHeader('Cache-Control','no-store'); next(); });
  router.get('/', (req, res, next) => {
    try {
      const query = z.object({ kind: z.enum(kinds).default('proposal'),
        offset: z.coerce.number().int().min(0).max(100000).default(0),
        limit: z.coerce.number().int().min(1).max(100).default(25) }).strict().parse(req.query);
      const systems = load(); const rows = systems.rows(query.kind);
      res.json({ summary: systems.crosswalk.summary, kind:query.kind, total:rows.length,
        rows:rows.slice(query.offset, query.offset+query.limit), planningOnly:true });
    } catch (error) { if(error instanceof z.ZodError) res.status(400).json({error:'Invalid catalog query'}); else next(error); }
  });
  router.post('/plan', (req, res, next) => {
    try {
      const request = superbotPlanSchema.parse(req.body);
      const result = load().plan(request);
      res.status(result.status==='not_found' ? 404 : result.status==='coordination_plan_ready' ? 200 : 409).json(result);
    } catch (error) { if(error instanceof z.ZodError) res.status(400).json({error:'Invalid plan request'}); else next(error); }
  });
  router.use((error: Error, _req: unknown, res: import('express').Response, _next: unknown) => {
    // No server paths or untrusted source text exposed as executable advice.
    res.status(503).json({error:'Superbot catalog unavailable or stale; regenerate and verify the crosswalk.', planningOnly:true});
  });
  return router;
}
