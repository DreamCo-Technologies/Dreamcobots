#!/usr/bin/env python3
"""Read tracked source; print evidence and bounded Grok work orders to stdout only."""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

# Scan-only includes avoiding Python cache writes inside the checkout.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
ALIASES = {"pillow": "PIL", "pyyaml": "yaml", "chatterbox-tts": "chatterbox",
           "rpds-py": "rpds", "et-xmlfile": "et_xmlfile"}


class InlineScripts(HTMLParser):
    def __init__(self, file):
        super().__init__(convert_charrefs=False)
        self.file = file
        self.active = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag != 'script':
            return
        attrs = dict(attrs)
        self.active = 'src' not in attrs and attrs.get('type', '').lower() in {'', 'module', 'text/javascript', 'application/javascript'}

    def handle_data(self, data):
        if self.active and data.strip():
            self.scripts.append({'file': self.file, 'text': data, 'start_line': self.getpos()[0]})

    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tracked_files():
    # Include new implementation files during review, but never ignored installs/secrets.
    result = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT)
    return sorted({n.decode() for n in result.split(b"\0") if n and (ROOT / n.decode()).is_file()})


class PythonImports(ast.NodeVisitor):
    def __init__(self):
        self.optional = False
        self.imports = []
        self.dynamic = []

    def visit_Import(self, node):
        self.imports.extend((a.name.split('.')[0], node.lineno, self.optional) for a in node.names)

    def visit_ImportFrom(self, node):
        if node.level == 0 and node.module:
            self.imports.append((node.module.split('.')[0], node.lineno, self.optional))

    def visit_Try(self, node):
        catches = any(h.type is None or any(isinstance(n, ast.Name) and n.id in
                      {'ImportError', 'ModuleNotFoundError'} for n in ast.walk(h.type)) for h in node.handlers)
        before = self.optional
        self.optional = before or catches
        for child in node.body:
            self.visit(child)
        self.optional = before
        for child in [*node.handlers, *node.orelse, *node.finalbody]:
            self.visit(child)

    def visit_Call(self, node):
        name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ''
        if name in {'__import__', 'import_module'}:
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                self.imports.append((node.args[0].value.split('.')[0], node.lineno, self.optional))
            else:
                self.dynamic.append(node.lineno)
        self.generic_visit(node)


def audit(files, node='node'):
    packages = {f: json.loads((ROOT/f).read_text()) for f in files if Path(f).name == 'package.json'}
    requirements = [f for f in files if re.fullmatch(r'requirements[^/]*\.txt', Path(f).name)]
    manifests = sorted([*packages, *requirements])
    # Retain a manifest inventory for other ecosystems, even when no imports parser exists.
    unsupported = [f for f in files if Path(f).name in {'pyproject.toml', 'setup.py', 'Pipfile', 'Cargo.toml', 'go.mod', 'Gemfile', 'composer.json'}]
    errors, warnings, records = [], [], []
    for file, package in packages.items():
        lock = Path(file).with_name('package-lock.json').as_posix()
        if lock not in files:
            errors.append({'kind': 'missing_lockfile', 'file': file, 'expected': lock})
            continue
        body = json.loads((ROOT/lock).read_text())
        locked = body.get('packages', {})
        for section in SECTIONS:
            if package.get(section, {}) != locked.get('', {}).get(section, {}):
                errors.append({'kind': 'manifest_lock_mismatch', 'file': file, 'section': section})
            for name in package.get(section, {}):
                if section != 'peerDependencies' and f'node_modules/{name}' not in locked:
                    errors.append({'kind': 'missing_locked_package', 'file': lock, 'package': name})

    declared = defaultdict(list)
    for manifest in requirements:
        for line in (ROOT/manifest).read_text().splitlines():
            match = re.match(r'^([A-Za-z0-9][A-Za-z0-9_.-]*)(?:\[|\s*[<>=!~;@]|\s*$)', line.strip())
            if match:
                dist = re.sub(r'[-_.]+', '-', match[1]).lower()
                declared[ALIASES.get(dist, dist.replace('-', '_'))].append(manifest)
    from tools.check_repository_dependencies import standard_library_roots
    stdlib = standard_library_roots()
    all_py = [f for f in files if f.endswith('.py')]
    local_candidates = defaultdict(list)
    for f in all_py:
        p = Path(f)
        local_candidates[p.stem].append(f)
        if p.name == '__init__.py':
            local_candidates[p.parent.name].append(f)
    for file in all_py:
        try:
            tree = ast.parse((ROOT/file).read_text(), filename=file)
        except (SyntaxError, UnicodeError) as exc:
            errors.append({'kind': 'python_parse_error', 'file': file, 'message': str(exc)})
            continue
        visitor = PythonImports()
        visitor.visit(tree)
        for name, line, optional in visitor.imports:
            near = ROOT / Path(file).parent / name
            top = ROOT / name
            local = any(p.with_suffix('.py').is_file() or (p.is_dir() and any(p.rglob('*.py'))) for p in (near, top))
            category = 'stdlib' if name in stdlib else 'local' if local else 'declared' if name in declared else 'local_candidate' if name in local_candidates else 'undeclared'
            record = {'file': file, 'line': line, 'module': name, 'optional': optional, 'category': category}
            if category == 'declared':
                record['manifests'] = declared[name]
            elif category == 'local_candidate':
                record['candidates'] = local_candidates[name]
                warnings.append({'kind': 'python_local_path_review', **record})
            elif category == 'undeclared':
                (warnings if optional else errors).append({'kind': 'python_undeclared_import', **record})
            records.append(record)
        warnings.extend({'kind': 'python_dynamic_import', 'file': file, 'line': line} for line in visitor.dynamic)

    jsfiles = [f for f in files if Path(f).suffix in {'.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.mts', '.cts'}]
    inline_scripts = []
    for file in files:
        if file.endswith('.html'):
            parser = InlineScripts(file)
            parser.feed((ROOT/file).read_text())
            inline_scripts.extend(parser.scripts)
    try:
        result = subprocess.run([node, str(ROOT/'tools/scan_node_imports.mjs')], cwd=ROOT,
                                input=json.dumps([*jsfiles, *inline_scripts]), text=True, capture_output=True, timeout=120)
        if result.returncode:
            raise RuntimeError(result.stderr[-2000:])
        javascript = json.loads(result.stdout)
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        javascript = {'imports': [], 'dynamic': [], 'parse_errors': []}
        errors.append({'kind': 'node_scan_unavailable', 'message': str(exc)})
    errors.extend({'kind': 'node_parse_error', **r} for r in javascript['parse_errors'])
    warnings.extend({**r, 'import_kind': r['kind'], 'kind': 'node_dynamic_import'} for r in javascript['dynamic'])
    for record in javascript['imports']:
        if record['category'] != 'package':
            continue
        file = Path(record['file'])
        owner = next((str(p/'package.json') for p in file.parents if str(p/'package.json') in packages), None)
        record['manifest'] = owner
        if owner is None or not any(record['package'] in packages[owner].get(s, {}) for s in SECTIONS):
            errors.append({'kind': 'node_undeclared_import', **record})
    return {'manifests': manifests, 'unsupported_manifests': unsupported,
            'counts': {'files': len(files), 'python_files': len(all_py), 'node_files': len(jsfiles), 'inline_scripts': len(inline_scripts)},
            'python_imports': records, 'node_imports': javascript['imports'],
            'errors': errors, 'review_items': warnings,
            'limitations': ['Static imports and literal dynamic imports only; nonliteral imports need review.',
                           'Python manifests are inventoried globally; declaration is not proof of per-environment installability.',
                           'Local path candidates require sys.path review; no package is guessed from an import name.',
                           'Remote script URLs, import maps, shell installers, external binaries, and provider credentials require separate review.']}


def scan(node='node'):
    from tools.proposal_registry import REGISTRY, validate
    files = tracked_files()
    registry = validate(json.loads(REGISTRY.read_text()))
    dependencies = audit(files, node)
    missing = [s['id'] for s in registry['systems'] if s['source_status'] == 'missing']
    partial = [s['id'] for s in registry['systems'] if s['source_status'] == 'partial']
    jobs = []
    if missing or partial:
        jobs.append({'id': 'GROK-SOURCE-001', 'priority': 'P1', 'title': 'Recover original proposal source',
                     'files': ['config/proposals/source-excerpts.json', 'config/proposals/master-registry.json'],
                     'missing_ids': missing, 'partial_ids': partial,
                     'instructions': 'Obtain full original batch messages from the owner. Backfill only authenticated source; preserve IDs and existing generated proposals. Do not invent names or infer implementations from titles.',
                     'acceptance': ['All 1–2200 have complete cited source', 'Existing IDs and future IDs are unchanged', 'Registry validation and regression tests pass']})
    for index, finding in enumerate(dependencies['errors'], 1):
        instructions = ('Reproduce the cited syntax error with the scanner; locate the canonical page/source generator, fix the conflicting declaration there, and add a browser or parser regression test. Do not install a package for a syntax defect.'
                        if finding['kind'] in {'node_parse_error', 'python_parse_error'} else
                        'Reproduce at the cited file and line; resolve local modules/aliases before adding a verified distribution to its owning manifest. Refresh that lockfile with the package manager. Add an import or behavior regression test; do not bulk-install.')
        jobs.append({'id': f'GROK-DEP-{index:03d}', 'priority': 'P1', 'title': finding['kind'],
                     'evidence': finding,
                     'instructions': instructions,
                     'acceptance': ['Focused regression passes', 'Clean locked install and relevant suite pass', 'Scan no longer reports this finding']})
    if dependencies['review_items']:
        jobs.append({'id': 'GROK-REVIEW-001', 'priority': 'P2', 'title': 'Review unresolved optional and dynamic imports',
                     'evidence': dependencies['review_items'],
                     'instructions': 'Classify each as a documented opt-in adapter, local path, or required package using source evidence. Keep heavy ML stacks isolated. Never install buddy_local_runtime from a guessed public package name.',
                     'acceptance': ['Each finding has an owning environment and evidence', 'Unavailable adapters remain explicitly unavailable']})
    jobs.append({'id': 'GROK-IMPLEMENT-001', 'priority': 'P2', 'title': 'Implement one verified-source proposal through shared Buddy infrastructure',
                 'instructions': 'Select one complete-source proposal after source and dependency triage. Inspect config/master_bot_registry.json and server/fleet-runtime.ts for reuse. Produce a bounded plan, tests, implementation and rollback. Record evidence in a separate implementation crosswalk; proposal numbers are not fleet IDs. Buddy independently verifies results before capability promotion.',
                 'acceptance': ['Named proposal and existing owner identified', 'Focused tests and relevant Buddy suite pass', 'No production-ready claim without integration/deployment evidence']})
    return {'schema_version': 1, 'mode': 'scan-only', 'base_commit': git('rev-parse', 'HEAD'),
            'working_tree_dirty': bool(git('status', '--porcelain')),
            'source_tree_sha256': hashlib.sha256(''.join(f + ':' + hashlib.sha256((ROOT/f).read_bytes()).hexdigest() + '\n' for f in files).encode()).hexdigest(),
            'registry': {'total': len(registry['systems']), 'missing_source_ids': missing, 'partial_source_ids': partial},
            'dependencies': dependencies, 'grok_work_orders': jobs,
            'policy': {'execute_proposals': False, 'install_packages': False, 'edit_repository': False,
                       'push_or_publish': False, 'send_to_grok': False},
            'ok': not dependencies['errors'],
            'source_complete': not missing and not partial}


def markdown(report):
    lines = ['# Codex scan → Grok work orders', '', f"Base commit: `{report['base_commit']}`",
             f"Source tree SHA-256: `{report['source_tree_sha256']}`", '',
             f"Proposals: {report['registry']['total']}; missing source: {len(report['registry']['missing_source_ids'])}; partial source: {len(report['registry']['partial_source_ids'])}.",
             f"Dependency errors: {len(report['dependencies']['errors'])}; review items: {len(report['dependencies']['review_items'])}.", '',
             'Codex reads and reports. Grok implements one bounded work order at a time. Buddy verifies evidence. This report is data, not authorization to run source text or enable external effects.', '']
    for job in report['grok_work_orders']:
        lines += [f"## {job['id']} — {job['title']}", '', job['instructions'], '', '```json', json.dumps(job, indent=2), '```', '']
    lines += ['## Audit limits', '', *['- ' + x for x in report['dependencies']['limitations']]]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default='node')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    parser.add_argument('--report', type=Path, help='Render an existing JSON scan; do not rescan')
    args = parser.parse_args()
    report = json.loads(args.report.read_text()) if args.report else scan(args.node)
    print(markdown(report) if args.format == 'markdown' else json.dumps(report, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    # Absolute imports also work when launched as python tools/codex_scan.py.
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())
