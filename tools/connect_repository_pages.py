#!/usr/bin/env python3
"""Connect every static page to Buddy's shared information actions and command center."""
import argparse
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
LOADER = '''\n// Shared repository controls are loaded once after the page is ready.
(() => {
  if (document.querySelector('script[data-repository-actions]')) return;
  const script = document.createElement('script');
  script.src = new URL('repository-actions.js', document.currentScript.src).href;
  script.dataset.repositoryActions = 'true';
  document.head.appendChild(script);
})();
'''

def connected(text):
    return bool(re.search(r'<script[^>]+src=["\'][^"\']*(?:nav|desk-chrome|repository-actions)\.js(?:[?][^"\']*)?["\']', text))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    missing = []
    for name in ('nav.js', 'desk-chrome.js'):
        p = ROOT / 'website' / name
        if 'data-repository-actions' not in p.read_text():
            if args.check: missing.append(name)
            else: p.write_text(p.read_text() + LOADER)
    for p in sorted((ROOT / 'website').rglob('*.html')):
        text = p.read_text()
        if connected(text): continue
        if args.check:
            missing.append(p.name)
            continue
        relative = '../' * (len(p.relative_to(ROOT / 'website').parts) - 1)
        script = f'<script src="{relative}repository-actions.js" data-repository-actions="true" defer></script>'
        if '</body>' not in text.lower(): raise ValueError(f'No body closing tag: {p}')
        text = re.sub(r'</body>', script + '\n</body>', text, count=1, flags=re.I)
        p.write_text(text)
    if missing: raise SystemExit('Disconnected pages: ' + ', '.join(missing))
    print('All website pages connect to shared repository controls')
if __name__ == '__main__': main()
