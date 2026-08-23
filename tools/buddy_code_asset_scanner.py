"""Inventory existing DreamCo code assets and emit training/benchmark candidates.

This scanner intentionally indexes files and metadata rather than copying source into prompts.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'buddy-code-assets'
EXTENSIONS={'.py','.ts','.tsx','.js','.jsx','.java','.kt','.kts','.go','.rs','.cpp','.c','.cs','.swift','.html','.css','.sql','.json','.yaml','.yml'}
KEYWORDS={
 'simulation':['simulation','simulator','scenario','sandbox'],
 'website':['website','web','landing','page','site'],
 'app':['app','application','dashboard','mobile'],
 'coding_library':['library','sdk','framework','adapter','component'],
 'workflow':['workflow','pipeline','orchestration','automation'],
 'benchmark_harness':['benchmark','eval','evaluation','test_suite'],
 'generator':['generator','scaffold','builder','template'],
}

def classify(path: Path, text: str) -> list[str]:
    s=(str(path)+' '+text[:10000]).lower()
    scores={k:sum(1 for word in words if word in s) for k,words in KEYWORDS.items()}
    return [k for k,v in sorted(scores.items(), key=lambda x:-x[1]) if v][:4] or ['production_feature']

def main():
    assets=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in EXTENSIONS: continue
        if any(part in {'.git','node_modules','dist','build','coverage','__pycache__'} for part in p.parts): continue
        try: text=p.read_text(errors='ignore')
        except Exception: continue
        classes=classify(p,text)
        assets.append({'path':str(p.relative_to(ROOT)),'asset_classes':classes,'size_bytes':p.stat().st_size,'learning_actions':['capability_map','benchmark_map','sandbox_variant','regression_candidate']})
    OUT.mkdir(parents=True,exist_ok=True)
    result={'schema':'dreamco.buddy.code_asset_index.v1','asset_count':len(assets),'assets':assets}
    (OUT/'latest-index.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Indexed {len(assets)} code assets')
if __name__=='__main__': main()
