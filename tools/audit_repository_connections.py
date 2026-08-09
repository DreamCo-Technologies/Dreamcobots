#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / 'config/repository-system-connection-policy.json').read_text(encoding='utf-8'))
OUT = ROOT / 'config/generated/repository-system-connections.json'
MAP_OUT = ROOT / 'config/generated/repo-wide-connection-map.json'
BACKLOG_OUT = ROOT / 'config/generated/repo-connection-builder-backlog.json'
REPORT = ROOT / 'reports/REPOSITORY_SYSTEM_CONNECTIONS.md'
PATH_RE = re.compile(r"(?<![A-Za-z0-9_.-])((?:tools|tests|config|server|shared|client|website|App_bots|docs|\.github)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+)")
API_RE = re.compile(r'\{\s*name:\s*["\']([^"\']+)["\']\s*,\s*category:\s*["\']([^"\']+)["\']')


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback
    except Exception:
        return fallback


def scan_file(path: Path, source_class: str, required: bool = True):
    text = read_text(path)
    rows = []
    for ref in sorted(set(PATH_RE.findall(text))):
        ref = ref.rstrip('.,;:)]}')
        target = ROOT / ref
        generated = ref.startswith('config/generated/') or ref.startswith('website/data/') or ref.startswith('tmp/')
        state = 'resolved' if target.exists() else ('generated_at_runtime' if generated else 'missing')
        rows.append({'source': str(path.relative_to(ROOT)), 'source_class': source_class, 'reference': ref, 'state': state, 'required': required})
    return rows


def collect_strings(value, key=None):
    found = set()
    if isinstance(value, dict):
        for k, v in value.items():
            if key is None or k == key:
                if isinstance(v, str): found.add(v)
            found |= collect_strings(v, key)
    elif isinstance(value, list):
        for item in value: found |= collect_strings(item, key)
    return found


def builders(entity_class: str, state: str):
    assignment = POLICY['builder_assignment']
    if state == 'duplicate': return assignment['duplicate']
    if state == 'missing_dependency': return assignment['dependency']
    if entity_class in {'bot', 'capability'}: return assignment['bot_or_capability']
    if entity_class == 'division': return assignment['division']
    if entity_class == 'API/integration': return assignment['API/integration']
    if entity_class in {'tool', 'workflow'}: return assignment['tool_or_workflow']
    return ['chief_architect', 'sandbox_qa_builder', 'release_reviewer']


def entity(entity_class, entity_id, name, state, evidence, source=None, parent=None, blocker=None):
    row = {
        'entity_class': entity_class, 'entity_id': entity_id, 'name': name, 'state': state,
        'source': source, 'parent': parent, 'evidence': evidence, 'blocker': blocker,
    }
    if state != 'working':
        row['needs_builder_bot'] = state not in {'generated_at_runtime'}
        row['builder_team'] = builders(entity_class, state) if row['needs_builder_bot'] else []
        row['next_action'] = {
            'disconnected': 'connect to canonical registry/router and add sandbox evidence',
            'partial': 'close missing connection stages and retest',
            'duplicate': 'reconcile to one canonical owner without losing unique capability',
            'missing_dependency': 'restore/replace dependency and run affected tests',
            'needs_builder_bot': 'implement smallest shared repair and retest',
            'external_adapter_unverified': 'verify authorized adapter in sandbox/staging before live claim',
            'generated_at_runtime': 'run canonical builder and preserve generated evidence',
        }.get(state, 'measure and repair')
    else:
        row['needs_builder_bot'] = False
        row['builder_team'] = []
        row['next_action'] = 'keep covered by regression and freshness checks'
    return row


def main() -> int:
    # Legacy reference-integrity audit retained for Full System Certification compatibility.
    references = []
    important = [
        (ROOT / 'tools/run_everything_now.py', 'Run Everything Now steps', True),
        (ROOT / 'tools/build_full_system_certification.py', 'Full System Certification dependencies', True),
        (ROOT / 'package.json', 'package scripts', True),
        (ROOT / 'config/run-everything-now.json', 'Run Everything config', True),
    ]
    for path, source_class, required in important:
        if path.exists(): references.extend(scan_file(path, source_class, required))
        else: references.append({'source': str(path.relative_to(ROOT)), 'source_class': source_class, 'reference': str(path.relative_to(ROOT)), 'state': 'missing', 'required': required})
    for folder, pattern, source_class in [
        (ROOT / '.github/workflows', '*.yml', 'workflow run commands'),
        (ROOT / '.github/agents', '*.agent.md', 'agent command references')
    ]:
        if folder.exists():
            for path in sorted(folder.glob(pattern)): references.extend(scan_file(path, source_class, False))

    ref_counts = Counter(r['state'] for r in references)
    ref_blockers = [r for r in references if r['required'] and r['state'] == 'missing']

    # Build shared evidence corpora once.
    package_text = read_text(ROOT / 'package.json')
    run_text = read_text(ROOT / 'tools/run_everything_now.py')
    workflow_text = '\n'.join(read_text(p) for p in sorted((ROOT / '.github/workflows').glob('*.yml'))) if (ROOT / '.github/workflows').exists() else ''
    tests_text = '\n'.join(read_text(p) for p in sorted((ROOT / 'tests').glob('*')) if p.is_file()) if (ROOT / 'tests').exists() else ''
    routes_text = read_text(ROOT / 'server/routes.ts') + '\n' + read_text(ROOT / 'server/fleet-runtime.ts')
    fleet_generator_text = read_text(ROOT / 'tools/generate_bot_fleet_catalog.ts')
    generated_catalog_path = ROOT / 'config/generated/bots.catalog.json'
    generated_catalog = read_json(generated_catalog_path, {})
    generated_catalog_text = json.dumps(generated_catalog).lower() if generated_catalog else ''
    generated_slugs = {s.lower() for s in collect_strings(generated_catalog, 'slug')}
    runtime_connections_path = ROOT / 'config/generated/runtime-connection-readiness.json'
    runtime_connections_text = json.dumps(read_json(runtime_connections_path, {})).lower()

    entities = []
    bot_occurrences = defaultdict(list)
    bot_rows = []
    division_rows = []
    app_dir = ROOT / 'App_bots'
    if not app_dir.exists():
        entities.append(entity('critical dependency', 'App_bots', 'App_bots', 'missing_dependency', ['canonical bot source root absent'], source='App_bots', blocker='canonical bot source root missing'))
    else:
        for path in sorted(app_dir.glob('*.json')):
            payload = read_json(path, {})
            division = str(payload.get('division') or path.stem)
            bots = payload.get('bots') if isinstance(payload.get('bots'), list) else []
            division_rows.append((division, path, len(bots)))
            for bot in bots:
                if not isinstance(bot, dict): continue
                slug = str(bot.get('slug') or '').strip()
                if not slug: continue
                bot_occurrences[slug].append(str(path.relative_to(ROOT)))
                bot_rows.append((division, path, bot))

    # Divisions.
    for division, path, bot_count in division_rows:
        shard = ROOT / 'website/data/bot-fleet' / f'{division}.json'
        evidence = [f'source={path.relative_to(ROOT)}', f'declared_bots={bot_count}']
        if shard.exists(): evidence.append(f'generated_shard={shard.relative_to(ROOT)}')
        if shard.exists() and bot_count > 0:
            state = 'working'
        elif bot_count > 0:
            state = 'partial'
        else:
            state = 'disconnected'
        entities.append(entity('division', f'division:{division}', division, state, evidence, source=str(path.relative_to(ROOT))))

    # Bots and declared capabilities.
    duplicate_slugs = {slug for slug, sources in bot_occurrences.items() if len(sources) > 1}
    for division, path, bot in bot_rows:
        slug = str(bot['slug'])
        low = slug.lower()
        evidence = [f'source={path.relative_to(ROOT)}', f'division={division}']
        if low in generated_slugs: evidence.append('generated fleet catalog contains slug')
        if low in routes_text.lower(): evidence.append('runtime/routes reference slug')
        if low in tests_text.lower(): evidence.append('test corpus references slug')
        if slug in duplicate_slugs:
            state = 'duplicate'; blocker = f'duplicate slug in {bot_occurrences[slug]}'
        elif low in generated_slugs and ('App_bots' in fleet_generator_text or low in routes_text.lower()):
            state = 'working'; blocker = None
        elif 'App_bots' in fleet_generator_text:
            state = 'partial'; blocker = 'source is discoverable by fleet generator but current generated/runtime evidence is incomplete'
        else:
            state = 'disconnected'; blocker = 'no canonical fleet generator/router evidence found'
        entities.append(entity('bot', f'bot:{slug}', bot.get('displayName') or slug, state, evidence, source=str(path.relative_to(ROOT)), parent=division, blocker=blocker))
        for index, capability in enumerate(bot.get('capabilities') or []):
            cap = str(capability).strip()
            if not cap: continue
            cap_low = cap.lower()
            cap_evidence = [f'parent_bot={slug}', f'declared_in={path.relative_to(ROOT)}']
            if cap_low in generated_catalog_text: cap_evidence.append('generated fleet catalog contains capability')
            cap_state = 'working' if state == 'working' and cap_low in generated_catalog_text else ('partial' if state != 'duplicate' else 'duplicate')
            entities.append(entity('capability', f'capability:{slug}:{index}', cap, cap_state, cap_evidence, source=str(path.relative_to(ROOT)), parent=slug, blocker=None if cap_state == 'working' else 'capability lacks complete current generated/runtime evidence'))

    # Tools: all repository tools are mapped, not just tools referenced by major orchestrators.
    referenced_text = '\n'.join([package_text, run_text, workflow_text])
    for path in sorted((ROOT / 'tools').glob('*')) if (ROOT / 'tools').exists() else []:
        if not path.is_file() or path.name.startswith('.'):
            continue
        rel = str(path.relative_to(ROOT))
        referenced = rel in referenced_text or path.name in referenced_text
        tested = path.name in tests_text or rel in tests_text
        evidence = [f'path={rel}', f'referenced_by_orchestrator={referenced}', f'referenced_by_tests={tested}']
        state = 'working' if referenced and (tested or path.name in run_text) else ('partial' if referenced else 'disconnected')
        entities.append(entity('tool', f'tool:{rel}', path.name, state, evidence, source=rel, blocker=None if state == 'working' else 'tool exists but canonical orchestration/test connection is incomplete'))

    # Workflows.
    wf_dir = ROOT / '.github/workflows'
    if wf_dir.exists():
        for path in sorted(wf_dir.glob('*.yml')):
            text = read_text(path)
            state = 'working' if 'jobs:' in text and ('run:' in text or 'uses:' in text) else 'partial'
            entities.append(entity('workflow', f'workflow:{path.name}', path.stem, state, [f'path={path.relative_to(ROOT)}'], source=str(path.relative_to(ROOT))))

    # Declared APIs/integrations remain unverified until explicit runtime evidence exists.
    api_path = ROOT / 'shared/api-registry.ts'
    seen_api = set()
    for name, category in API_RE.findall(read_text(api_path)):
        key = (name.lower(), category.lower())
        if key in seen_api: continue
        seen_api.add(key)
        low = name.lower()
        verified = low in runtime_connections_text and any(token in runtime_connections_text for token in ('runtime_verified', 'verified', 'connected'))
        state = 'working' if verified else 'external_adapter_unverified'
        evidence = [f'declared={api_path.relative_to(ROOT)}', f'category={category}', f'runtime_readiness_present={runtime_connections_path.exists()}']
        entities.append(entity('API/integration', f'api:{category}:{name}', name, state, evidence, source=str(api_path.relative_to(ROOT)), blocker=None if verified else 'authorized runtime connection evidence not proven'))

    # Critical referenced dependencies and generated artifacts.
    for row in references:
        if row['state'] == 'missing':
            entities.append(entity('critical dependency', f"dependency:{row['source']}->{row['reference']}", row['reference'], 'missing_dependency', [f"consumer={row['source']}"], source=row['source'], blocker='required referenced path missing'))
        elif row['state'] == 'generated_at_runtime':
            entities.append(entity('generated artifact', f"generated:{row['reference']}", row['reference'], 'generated_at_runtime', [f"consumer={row['source']}"], source=row['source']))

    # Make every non-working entity actionable.
    state_counts = Counter(row['state'] for row in entities)
    class_counts = Counter(row['entity_class'] for row in entities)
    backlog = [row for row in entities if row['state'] != 'working' and row.get('needs_builder_bot')]
    backlog_by_team = defaultdict(int)
    for row in backlog:
        for worker in row.get('builder_team', []): backlog_by_team[worker] += 1

    map_payload = {
        'schema': 'dreamco.repo_wide_connection_map.v2',
        'entity_count': len(entities),
        'entity_class_counts': dict(sorted(class_counts.items())),
        'state_counts': dict(sorted(state_counts.items())),
        'working_count': state_counts.get('working', 0),
        'nonworking_count': len(entities) - state_counts.get('working', 0),
        'builder_backlog_count': len(backlog),
        'duplicate_bot_slugs': sorted(duplicate_slugs),
        'entities': entities,
        'truth_boundary': POLICY['truth_rule']
    }
    backlog_payload = {
        'schema': 'dreamco.repo_connection_builder_backlog.v1',
        'backlog_count': len(backlog),
        'builder_load': dict(sorted(backlog_by_team.items())),
        'parallel_rule': 'independent canonical owners may be worked in parallel; same-owner changes serialize and reconcile',
        'gaps': backlog,
        'truth_boundary': POLICY['truth_rule']
    }
    legacy_payload = {
        'schema': 'dreamco.repository_system_connections.v2',
        'reference_count': len(references),
        'state_counts': dict(ref_counts),
        'release_blocker_count': len(ref_blockers) + len(duplicate_slugs),
        'release_blockers': ref_blockers + [{'type': 'duplicate canonical bot slug', 'slug': s, 'sources': bot_occurrences[s]} for s in sorted(duplicate_slugs)],
        'references': references,
        'entity_summary': {'entities': len(entities), 'states': dict(sorted(state_counts.items())), 'builder_backlog': len(backlog)},
        'ok': not ref_blockers and not duplicate_slugs,
        'truth_boundary': POLICY['truth_rule']
    }

    OUT.parent.mkdir(parents=True, exist_ok=True); REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(legacy_payload, indent=2) + '\n', encoding='utf-8')
    MAP_OUT.write_text(json.dumps(map_payload, indent=2) + '\n', encoding='utf-8')
    BACKLOG_OUT.write_text(json.dumps(backlog_payload, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Repository System Connections', '',
        f"- References checked: **{len(references)}**", f"- Required missing references: **{len(ref_blockers)}**",
        f"- Repo-wide entities mapped: **{len(entities)}**", f"- Working: **{state_counts.get('working', 0)}**",
        f"- Builder backlog: **{len(backlog)}**", f"- Duplicate bot slugs: **{len(duplicate_slugs)}**", '', '## Connection states', ''
    ]
    for state, count in sorted(state_counts.items()): lines.append(f'- {state}: {count}')
    lines += ['', '## Entity classes', '']
    for kind, count in sorted(class_counts.items()): lines.append(f'- {kind}: {count}')
    if backlog:
        lines += ['', '## Builder backlog sample', '']
        for row in backlog[:300]: lines.append(f"- `{row['entity_id']}` → **{row['state']}** → {', '.join(row.get('builder_team', []))}")
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'ok': legacy_payload['ok'], 'references': len(references), 'entities': len(entities), 'states': dict(state_counts), 'builder_backlog': len(backlog), 'outputs': [str(OUT.relative_to(ROOT)), str(MAP_OUT.relative_to(ROOT)), str(BACKLOG_OUT.relative_to(ROOT))]}, indent=2))
    return 0 if legacy_payload['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
