import re,sys,hashlib,zipfile,io,uuid
from urllib.parse import urlparse
from ..common import parser,read_json,write_json,digest,validate

MAX_BYTES=5*1024*1024
MAX_ZIP_FILES=500
MAX_EXPANDED=25*1024*1024
MAX_RATIO=100
SECRET_PATTERNS=[
 re.compile(r'(?i)(aws_access_key_id|api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*[\'"]?[^\s,;\'"]+'),
 re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
 re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b'),
 re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b')]
PII_PATTERNS=[re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',re.I),re.compile(r'\b\d{3}-\d{2}-\d{4}\b')]
BLOCKED_HOSTS={"pastebin.com","1337x.to","thepiratebay.org"}
def scan(text):
    findings=[]; clean=text
    for pattern in SECRET_PATTERNS:
        clean,n=pattern.subn("[REDACTED_SECRET]",clean)
        if n:findings.append("SECRET_REDACTED")
    for pattern in PII_PATTERNS:
        clean,n=pattern.subn("[REDACTED_PII]",clean)
        if n:findings.append("PII_REDACTED")
    # High-entropy token-like strings are redacted only when long and mixed-class.
    token=re.compile(r'(?<![A-Za-z0-9])[A-Za-z0-9_+/=-]{32,}(?![A-Za-z0-9])')
    def entropy(s):
        from math import log2
        from collections import Counter
        c=Counter(s); return -sum((n/len(s))*log2(n/len(s)) for n in c.values())
    def sub(m):
        s=m.group(0)
        if len(set(s))>=12 and entropy(s)>=4.2:
            findings.append("HIGH_ENTROPY_TOKEN_REDACTED"); return "[REDACTED_HIGH_ENTROPY]"
        return s
    return token.sub(sub,clean),sorted(set(findings))
def main():
    a=parser("DreamCo Stage 1 policy gate").parse_args(); raw=read_json(a.input)
    text=raw.get("content",""); permission=raw.get("permission",{})
    findings=[]; code="ACCEPTED"; reason=""
    if not isinstance(text,str): code="INVALID_CONTENT"; text=""
    elif len(text.encode())>MAX_BYTES: code="FILE_TOO_LARGE"
    elif permission.get("authorized") is not True: code="PERMISSION_REQUIRED"
    elif permission.get("target_kind") not in {"user_owned","public_api","open_source","user_authorized_logs","user_authorized_workflow","user_authorized_schema"}: code="TARGET_NOT_ALLOWED"
    elif permission.get("bypass_requested") or permission.get("drm_circumvention") or permission.get("unauthorized_login_scraping"): code="PROHIBITED_ACCESS"
    elif permission.get("target_kind")=="open_source" and permission.get("license_id") not in {"MIT","Apache-2.0","BSD-2-Clause","BSD-3-Clause","ISC","0BSD"}: code="LICENSE_REVIEW_REQUIRED"
    else:
        host=urlparse(raw.get("source_url","")).hostname
        if host and host.lower() in BLOCKED_HOSTS: code="RESTRICTED_DOMAIN"
    if code=="ACCEPTED" and raw.get("archive_base64"):
        try:
            z=zipfile.ZipFile(io.BytesIO(__import__("base64").b64decode(raw["archive_base64"])))
            infos=z.infolist()
            if len(infos)>MAX_ZIP_FILES or sum(i.file_size for i in infos)>MAX_EXPANDED or any(i.file_size/max(i.compress_size,1)>MAX_RATIO for i in infos): code="ARCHIVE_LIMIT_EXCEEDED"
        except Exception: code="INVALID_ARCHIVE"
    clean,redactions=scan(text) if code=="ACCEPTED" else ("",[])
    findings.extend(redactions)
    result={"schema_version":"dreamco.artifact_manifest.v1","job_id":raw.get("job_id") or str(uuid.uuid4()),"status":"ACCEPTED" if code=="ACCEPTED" else "REJECTED","artifact_type":raw.get("artifact_type","auto"),"sha256":digest(clean),"sanitized_text":clean,"policy":{"decision":"PASS" if code=="ACCEPTED" else "BLOCK","audit_code":code,"findings":findings}}
    validate(result,"artifact_manifest.schema.json"); write_json(a.output,result)
    if code!="ACCEPTED": sys.exit(2)
if __name__=="__main__":main()
