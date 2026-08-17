"""Compile validated video evidence JSONL into an AI-readable package seed."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def compile_package(source: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows=[]
    for line in source.read_text().splitlines():
        if line.strip(): rows.append(json.loads(line))
    package_id=hashlib.sha256(source.read_bytes()).hexdigest()[:16]
    manifest={"schema":"dreamco.video.capability_package.v1","package_id":package_id,"source_manifest":str(source),"records":len(rows),"status":"compiled_seed","limitations":["semantic claims depend on validated upstream evidence"],"confidence_policy":"preserve source confidence"}
    (out_dir/"manifest.json").write_text(json.dumps(manifest,indent=2))
    with (out_dir/"knowledge.jsonl").open("w") as f:
        for row in rows:
            f.write(json.dumps({"video_id":row.get("video_id"),"claims":row.get("claims",[]),"evidence":row.get("evidence",[]),"confidence":row.get("confidence","unknown"),"timestamps":row.get("timestamps",[]),"source":row.get("source")},ensure_ascii=False)+"\n")

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("source",type=Path); p.add_argument("--output",type=Path,default=Path("artifacts/video_package")); a=p.parse_args(); compile_package(a.source,a.output)
