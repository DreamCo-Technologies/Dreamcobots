"""Audit an untrusted pull-request patch without executing PR code."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

SECRET_PATTERNS = {
 "HF_TOKEN": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
 "GITHUB_TOKEN": re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b"),
 "OPENAI_STYLE_KEY": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
 "AWS_ACCESS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
 "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
VANITY_PATTERNS = {
 "GUARANTEED_PERFORMANCE": re.compile(r"\b100%\s+guaranteed\b", re.I),
 "UNBEATABLE": re.compile(r"\bunbeatable\b", re.I),
 "AGI_ACHIEVED": re.compile(r"\bAGI\s+achieved\b", re.I),
 "ZERO_LATENCY": re.compile(r"\bzero\s+latency\b", re.I),
}
QUARANTINE_PARTS = ("staging_quarantine/", "staging-quarantine/", "resource_staging/")
EVIDENCE_NAMES = {"evidence_stamp.json", "model_evidence.json", "release_candidate.json"}

def fp(code, path, message):
 return hashlib.sha256(f"{code}\0{path}\0{message}".encode()).hexdigest()[:12]

def parse_patch(patch):
 files, additions, current, new_line = [], [], "", 0
 for line in patch.splitlines():
  if line.startswith("diff --git "):
   m = re.match(r"diff --git a/(.+) b/(.+)$", line)
   if m:
    current=m.group(2); files.append(current)
  elif line.startswith("@@"):
   m=re.search(r"\+(\d+)(?:,(\d+))?", line); new_line=int(m.group(1)) if m else 0
  elif line.startswith("+") and not line.startswith("+++"):
   additions.append((current,line[1:],new_line)); new_line+=1
  elif line.startswith(" ") and current: new_line+=1
 return sorted(set(files)), additions

def finding(gate, code, severity, path, line, message):
 return {"gate":gate,"code":code,"severity":severity,"path":path,"line":line or None,
         "message":message,"fingerprint":fp(code,path,message)}

def audit(patch, pr_number=None):
 files, additions=parse_patch(patch); findings=[]; issues=[]
 for path, text, line in additions:
  for code, pattern in SECRET_PATTERNS.items():
   if pattern.search(text):
    findings.append(finding("Code Trust Gate",code,"BLOCKER",path,line,
      "Possible credential material appears in added PR content. Revoke/rotate the credential and remove it from repository history."))
  for code, pattern in VANITY_PATTERNS.items():
   if pattern.search(text):
    findings.append(finding("Frontier Claim Trust Gate",code,"BLOCKER",path,line,
      "Unverified absolute performance claim. Replace it with a bounded, reproducible claim linked to benchmark evidence."))
  if any(part in path.lower() for part in QUARANTINE_PARTS):
   findings.append(finding("Clean-Room IP Gate","QUARANTINE_COMMIT","BLOCKER",path,line,
      "Quarantined source material must remain outside committed application, training, and release artifacts."))
  if text.startswith(("<<<<<<< ","=======" ,">>>>>>> ")):
   issues.append({"issue_type":"MERGE_CONFLICT_MARKER","priority":"CRITICAL","auto_fixable":False,
     "file":path,"line":line or None,"remediation":"Resolve conflict markers manually and rerun the complete test suite.",
     "fingerprint":fp("MERGE_CONFLICT_MARKER",path,"Conflict marker in added lines")})
 checkpoint_files=[p for p in files if p.startswith("checkpoints/")]
 if checkpoint_files and not any(Path(p).name in EVIDENCE_NAMES for p in files):
  findings.append(finding("Evidence Gate","CHECKPOINT_WITHOUT_EVIDENCE","BLOCKER","checkpoints/",0,
    "Checkpoint artifacts changed without a corresponding evidence manifest update. Bind exact weights, tokenizer, data hashes, and training run."))
 for path in [p for p in files if p.endswith("competitor_registry.json")]:
  for changed_path, value, line in additions:
   if changed_path==path and re.search(r'"(?:pinned_revision|revision)"\s*:\s*"(?:main|master|latest|HEAD)"',value,re.I):
    findings.append(finding("Baseline Reproducibility Gate","UNPINNED_COMPETITOR_REVISION","BLOCKER",path,line,
      "Competitor baseline revisions must be immutable commit SHAs, not branch names or moving tags."))
 status="CHANGES_REQUESTED" if any(x["severity"]=="BLOCKER" for x in findings) or issues else "REVIEW_REQUIRED"
 report={"schema":"dreamco.pr_audit_report.v1","system":"DreamCo PR Review & MR Issue Triage",
  "timestamp_utc":datetime.now(timezone.utc).isoformat(),"pull_request":pr_number,"review_status":status,
  "files_reviewed":len(files),"changed_files":files,"gate_findings":findings,"mr_issues_queue":issues,
  "execution_policy":"PR code was not checked out or executed by this trusted audit."}
 report["review_sha256"]=hashlib.sha256(json.dumps(report,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 return report

def render(report):
 lines=[f"## DreamCo Automated PR Review — {report['review_status']}",
  f"- Files reviewed: **{report['files_reviewed']}**",
  f"- Review report SHA-256: {report['review_sha256']}","","### Trust and contract findings"]
 if not report["gate_findings"]:
  lines.append("- No configured patch-level blocker was detected. This is not a full approval; CI and independent reviews remain required.")
 for x in report["gate_findings"]:
  loc=f" ({x['path']}:{x['line']})" if x["line"] else f" ({x['path']})"
  lines.append(f"- **{x['severity']} · {x['gate']} · {x['code']}**{loc}: {x['message']} [fingerprint {x['fingerprint']}]")
 lines.extend(["","### MR issue queue"])
 if not report["mr_issues_queue"]: lines.append("- No patch-level merge-marker issue detected.")
 for x in report["mr_issues_queue"]:
  lines.append(f"- **{x['priority']} · {x['issue_type']}** ({x['file']}:{x['line']}): {x['remediation']} [fingerprint {x['fingerprint']}]")
 lines.extend(["","> This patch scan does not approve a PR, prove clean-room originality, establish legal rights, or replace tests, CodeQL, human review, or branch protection."])
 return "\n".join(lines)+"\n"

def main():
 p=argparse.ArgumentParser(); p.add_argument("--diff-file",required=True,type=Path)
 p.add_argument("--pr-number",type=int); p.add_argument("--output-dir",type=Path,default=Path("artifacts/pr-audit"))
 a=p.parse_args(); report=audit(a.diff_file.read_text(encoding="utf-8",errors="replace"),a.pr_number)
 a.output_dir.mkdir(parents=True,exist_ok=True)
 (a.output_dir/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 (a.output_dir/"comment.md").write_text(render(report),encoding="utf-8")
 print(json.dumps({"review_status":report["review_status"],"files_reviewed":report["files_reviewed"],
  "findings":len(report["gate_findings"]),"mr_issues":len(report["mr_issues_queue"]),
  "report_sha256":report["review_sha256"]},indent=2))
 return 1 if report["review_status"]=="CHANGES_REQUESTED" else 0
if __name__=="__main__": raise SystemExit(main())
