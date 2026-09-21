#!/usr/bin/env python3
"""Index every tracked file by path; add searchable summaries for text documents."""
import argparse, json, os, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'website/data/repository-library.json'
def build():
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    entries = []
    for name in sorted(set(filter(None, paths))):
        p = ROOT / name
        if not p.is_file():
            continue
        category = ('Plans' if re.search(r'plan|roadmap|backlog|strategy|directive', name, re.I) else
                    'Documents' if p.suffix.lower() in {'.md', '.txt', '.rst'} else
                    'Bots' if name.startswith(('App_bots/', 'bots/')) else
                    'Build checks' if name.startswith(('.github/workflows/', 'tests/')) else
                    'Website' if name.startswith('website/') else 'Code & data')
        title, summary, words = p.name, '', ''
        # Index prose only. Never copy credentials, configuration values, or generated data.
        if p.suffix.lower() in {'.md', '.txt', '.rst'} and p.stat().st_size < 1_000_000:
            raw = p.read_text(errors='replace')
            match = re.search(r'^#\s+(.+)', raw, re.M)
            if match: title = match[1][:180]
            prose = re.sub(r'```.*?```', '', raw, flags=re.S)
            prose = re.sub(r'https?://\S+|[^\w\s.,:;!?/-]', ' ', prose)
            summary = ' '.join(prose.split())[:280]
            words = ' '.join(sorted(set(re.findall(r'[a-z][a-z0-9_-]{2,35}', prose.lower()))))
        entries.append({'path': name, 'title': title, 'kind': category, 'summary': summary, 'words': words})
    return {'schema': 'dreamco.repository-library.v1', 'repository': 'DreamCo-Technologies/Dreamcobots',
            'ref': os.environ.get('GITHUB_REF_NAME') or subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip(),
            'scope': 'Every tracked file by path; prose documents also have keyword search. Plans are grouped by filename. Generated bot pages are available in the specialist directory.', 'files': entries}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); args = ap.parse_args()
    text = json.dumps(build(), ensure_ascii=False, separators=(',', ':')) + '\n'
    if args.check:
        if not OUT.exists() or OUT.read_text() != text: raise SystemExit('Repository library is stale')
    else: OUT.write_text(text)
    print(f'Repository library: {len(json.loads(text)["files"])} tracked files')
if __name__ == '__main__': main()
