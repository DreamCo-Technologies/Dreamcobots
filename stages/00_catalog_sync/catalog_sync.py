"""Incremental append-only metadata catalog; metadata only, no media/transcript downloads."""
from __future__ import annotations
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_POLICY=ROOT/"contracts/license_policy.yaml"
DEFAULT_LEDGER=ROOT/"data/manifests/source_catalog.jsonl"
def canonical_hash(record:dict[str,Any])->str:
    payload={k:v for k,v in record.items() if k not in {"metadata_sha256","content_sha256","observed_at"}}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def load_policy(path:Path)->dict[str,Any]:
    import yaml
    data=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if data.get("schema")!="dreamco.source_license_policy.v1": raise ValueError("unsupported policy schema")
    return data
def _url_matches_prefix(url:str,prefix:str)->bool:
    url=url.strip(); prefix=prefix.strip()
    if prefix.endswith("="): return url.startswith(prefix) and len(url)>len(prefix)
    base=prefix.rstrip("/")
    return url==base or url.startswith(base+"/") or url.startswith(base+"?")
def registered_source(source_id:str,url:str,policy:dict[str,Any])->dict[str,Any]|None:
    from urllib.parse import urlparse
    host=(urlparse(url).hostname or "").lower()
    for row in policy.get("sources",[]):
        domains=[str(x).lower() for x in row.get("domains",[])]
        domain_match=any(host==d or host.endswith("."+d) for d in domains)
        id_match=source_id in row.get("catalog_source_ids",[])
        url_match=any(_url_matches_prefix(url,prefix) for prefix in row.get("allowed_url_prefixes",[]))
        if domain_match and id_match and url_match and row.get("catalog_metadata_allowed") is True:
            return row
    return None
def source_is_configured(source_id:str,url:str,policy:dict[str,Any])->bool:
    return registered_source(source_id,url,policy) is not None
def enumerate_source(url:str,timeout:int=1800)->list[dict[str,Any]]:
    result=subprocess.run(["yt-dlp","--flat-playlist","--dump-json","--no-warnings",url],check=True,capture_output=True,text=True,timeout=timeout)
    rows=[]
    for n,line in enumerate(result.stdout.splitlines(),1):
        if line.strip():
            try: rows.append(json.loads(line))
            except json.JSONDecodeError as exc: raise ValueError(f"invalid yt-dlp JSON at line {n}") from exc
    return rows
def normalize_item(item:dict[str,Any],url:str,source_id:str,expected_channel_id:str|None=None)->dict[str,Any]:
    video_id=str(item.get("id") or "").strip()
    if not video_id: raise ValueError("catalog item missing video ID")
    observed_channel=str(item.get("channel_id") or item.get("playlist_channel_id") or "").strip()
    if expected_channel_id and observed_channel != expected_channel_id:
        raise PermissionError("video channel ID does not match the registered official channel")
    lic=str(item.get("license") or "").strip()
    return {"schema":"dreamco.source_catalog_record.v1","source_id":source_id,"source_url":url,"video_id":video_id,
      "published_at":item.get("release_date") or item.get("upload_date") or item.get("timestamp"),"duration":item.get("duration"),
      "license_tag":lic or "UNKNOWN_UNVERIFIED","license_record_verified":False,
      "license_evidence_url":None,"license_evidence_path":None,"license_evidence_sha256":None,"license_review_status":"needs_human",
      "license_reviewer_id":None,"license_reviewed_at":None,"commercial_training_evidence_ref":None,
      "transcript_status":"NOT_FETCHED",
      "catalog_policy_status":"METADATA_ONLY_PENDING_ITEM_RIGHTS","observed_at":datetime.now(timezone.utc).isoformat()}
def read_ledger(path:Path)->dict[str,str]:
    latest={}
    if not path.exists(): return latest
    for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if line.strip():
            try: row=json.loads(line)
            except json.JSONDecodeError as exc: raise ValueError(f"invalid ledger JSON at line {n}") from exc
            latest[f"{row.get('source_id')}:{row.get('video_id')}"]=str(row.get("metadata_sha256") or row.get("content_sha256") or "")
    return latest
def sync_sources(sources:list[dict[str,str]],ledger:Path=DEFAULT_LEDGER,policy_path:Path=DEFAULT_POLICY,enumerator=enumerate_source)->dict[str,Any]:
    policy=load_policy(policy_path); ledger.parent.mkdir(parents=True,exist_ok=True); latest=read_ledger(ledger); pending=[]; seen=set(); enumerated_total=0
    for source in sources:
        url,source_id=source["url"],source["source_id"]
        source_policy=registered_source(source_id,url,policy)
        if source_policy is None: raise PermissionError(f"source not allowlisted for metadata cataloging: {source_id}")
        expected_channel_id=source_policy.get("official_channel_id")
        items=enumerator(url)
        if not items: raise ValueError(f"source enumeration returned zero items for {source_id}; refusing an empty sync")
        enumerated_total += len(items)
        for item in items:
            row=normalize_item(item,url,source_id,expected_channel_id); key=f"{source_id}:{row['video_id']}"
            if key in seen: continue
            seen.add(key); digest=canonical_hash(row)
            if latest.get(key)==digest: continue
            row["metadata_sha256"]=digest; pending.append(row)
    with ledger.open("a",encoding="utf-8") as stream:
        for row in pending: stream.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n")
    return {"schema":"dreamco.source_catalog_sync_report.v1","sources_scanned":len(sources),"enumerated_items":enumerated_total,"new_or_updated_records":len(pending),
      "ledger_records":sum(bool(x.strip()) for x in ledger.read_text(encoding="utf-8").splitlines()),"append_only":True,
      "media_downloaded":False,"transcripts_fetched":False}
def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--source",action="append",default=[],metavar="ID=URL")
    p.add_argument("--policy",type=Path,default=DEFAULT_POLICY); p.add_argument("--ledger",type=Path,default=DEFAULT_LEDGER); a=p.parse_args(); sources=[]
    for value in a.source:
        sid,sep,url=value.partition("=")
        if not sep or not sid.strip() or not url.strip(): p.error("--source must use ID=URL")
        sources.append({"source_id":sid.strip(),"url":url.strip()})
    if not sources: p.error("provide at least one --source ID=URL")
    print(json.dumps(sync_sources(sources,a.ledger,a.policy),indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
