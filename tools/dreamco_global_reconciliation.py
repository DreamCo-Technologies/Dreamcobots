#!/usr/bin/env python3
"""Evidence-first inventory for DreamCo Markdown, chat exports, and PR metadata.

This tool inventories source material; it never merges PRs or claims runtime proof.
ChatGPT conversations must be exported/approved and placed under the configured
chat source directory. GitHub Actions cannot silently read private ChatGPT chats.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "dreamco-reconciliation"
CHAT_ROOT = ROOT / "governance" / "dreamco-chat-sources"
EVIDENCE_MAP = ROOT / "governance" / "dreamco-requirement-evidence.json"
IGNORE = {".git", "node_modules", ".venv", "venv", "dist", "build", "vendor"}
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots")

def stable_id(source: str, text: str) -> str:
    digest = hashlib.sha256((source + "\0" + re.sub(r"\s+", " ", text).strip()).encode()).hexdigest()[:14]
    return "DCO-" + digest.upper()

def tracked_markdown() -> list[Path]:
    import subprocess
    try:
        raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        paths = [ROOT / p.decode() for p in raw.split(b"\0") if p]
    except Exception:
        paths = [p for p in ROOT.rglob("*") if p.is_file()]
    return sorted(p for p in paths if p.suffix.lower() in {".md", ".mdx"}
                  and not (set(p.relative_to(ROOT).parts) & IGNORE))

def extract_requirements(path: Path) -> list[dict]:
    rel = path.relative_to(ROOT).as_posix()
    try: lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError: return []
    rows, section = [], ""
    for number, line in enumerate(lines, 1):
        s = line.strip()
        if not s: continue
        if re.match(r"^#{1,6}\s+", s): section = re.sub(r"^#{1,6}\s+", "", s)
        if (re.match(r"^[-*+]\s+\[[ xX]\]\s+", s) or
            re.match(r"^[-*+]\s+", s) or re.match(r"^\d+[.)]\s+", s)):
            body = re.sub(r"^[-*+]\s+(?:\[[ xX]\]\s+)?|^\d+[.)]\s+", "", s).strip()
            if len(body) >= 12:
                rows.append({"requirement_id":stable_id(rel, body),"source_type":"markdown",
                             "source_path":rel,"line":number,"section":section,"text":body})
    return rows

def github_pages(endpoint: str) -> list[dict]:
    if not TOKEN: return []
    url = "https://api.github.com/repos/" + REPO + endpoint
    all_rows = []
    while url:
        req = urllib.request.Request(url, headers={"Authorization":"Bearer "+TOKEN,
            "Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            all_rows.extend(data if isinstance(data, list) else [])
            link = response.headers.get("Link", "")
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = match.group(1) if match else None
    return all_rows

def chat_sources() -> list[dict]:
    rows = []
    if not CHAT_ROOT.exists(): return rows
    for p in sorted(CHAT_ROOT.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".md",".mdx",".json",".txt"}: continue
        try: raw = p.read_text(encoding="utf-8", errors="replace")
        except OSError: continue
        rel = p.relative_to(ROOT).as_posix()
        if p.suffix.lower()==".json":
            try:
                obj=json.loads(raw)
                raw=json.dumps(obj,ensure_ascii=False,sort_keys=True)
            except json.JSONDecodeError: pass
        rows.append({"source_id":stable_id(rel,raw[:5000]),"source_type":"chat_export",
                     "source_path":rel,"sha256":hashlib.sha256(raw.encode()).hexdigest(),
                     "characters":len(raw),"status":"ingested_export_only"})
    return rows

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir", default=str(OUT))
    args=ap.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    md_files=tracked_markdown()
    requirements=[r for p in md_files for r in extract_requirements(p)]
    chats=chat_sources()
    prs=[]
    try:
        prs=github_pages("/pulls?state=all&per_page=100&sort=updated&direction=desc")
        prs=[{"number":p["number"],"title":p["title"],"state":p["state"],
              "draft":p.get("draft",False),"merged_at":p.get("merged_at"),
              "updated_at":p.get("updated_at"),"base":p["base"]["ref"],
              "head":p["head"]["ref"],"head_sha":p["head"]["sha"],
              "html_url":p["html_url"],"changed_files":p.get("changed_files"),
              "mergeable_state":p.get("mergeable_state")} for p in prs]
    except Exception as exc:
        (out/"github-pr-inventory-error.txt").write_text(str(exc)+"\n")
    evidence={}
    if EVIDENCE_MAP.exists():
        try: evidence=json.loads(EVIDENCE_MAP.read_text(encoding="utf-8"))
        except Exception: evidence={}
    summary={"generated_at":datetime.now(timezone.utc).isoformat(),
      "repository":REPO,"markdown_file_count":len(md_files),
      "markdown_requirement_count":len(requirements),"chat_export_count":len(chats),
      "pull_request_count":len(prs),"open_pr_count":sum(p["state"]=="open" for p in prs),
      "requirements_with_evidence_mapping":len(evidence.get("requirements",{})),
      "limitations":["Only repository-visible Markdown is inventoried.",
        "ChatGPT chats are included only when explicitly exported/approved into governance/dreamco-chat-sources.",
        "PR metadata is not a three-way merge or conflict-resolution proof.",
        "No PR is merged, no branch is rewritten, and no deployment is triggered."]}
    payloads={"summary.json":summary,"markdown-requirements.json":{"requirements":requirements},
      "chat-source-inventory.json":{"sources":chats},"pull-request-inventory.json":{"pull_requests":prs}}
    for name,obj in payloads.items():
        (out/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": sys.exit(main())
