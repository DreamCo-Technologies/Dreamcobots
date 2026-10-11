"""Copy only explicitly reviewed public demo inputs into the Pages artifact."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'bootcamp.json': 'config/buddy-bootcamp-curriculum-v1.json',
    'model-catalog.json': 'buddy/openrouter/client_model_catalog.json',
    'model-registry.json': 'config/buddy/500-model-registry.json',
    'packages.json': 'buddy/store/packages.json',
}


def generate(root=ROOT, check=False):
    stale=[]
    for name, source in SOURCES.items():
        content=(root/source).read_text()
        json.loads(content)
        target=root/'website/data/live-demos'/name
        if not target.exists() or target.read_text()!=content:
            stale.append(name)
            if not check:
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(content)
    return stale


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    stale=generate(check=args.check)
    print(json.dumps({'ok':not args.check or not stale,'stale':stale}))
    raise SystemExit(1 if args.check and stale else 0)
