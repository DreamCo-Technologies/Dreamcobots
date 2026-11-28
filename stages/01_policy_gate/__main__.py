import re,sys,zipfile,io,uuid,base64,ipaddress
from pathlib import Path
from urllib.parse import urlparse
from ..common import parser,read_json,write_json,digest,validate
MAX_INPUT_BYTES=13*1024*1024
MAX_BYTES=5*1024*1024
MAX_ARCHIVE_ENCODED=7*1024*1024
MAX_ZIP_FILES=500
MAX_EXPANDED=25*1024*1024
MAX_RATIO=100
SECRET_PATTERNS=[
 re.compile(r'(?i)(aws_access_key_id|api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*[\'"]?[^\s,;\'"]+'),
 re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
 re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b'),
 re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'),
 re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
PII_PATTERNS=[
 re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',re.I),
 re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
 re.compile(r'(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)')]
BLOCKED_HOSTS={"pastebin.com","1337x.to","thepiratebay.org"}
def scan(text):
 findings=[]; clean=text
 for pattern in SECRET_PATTERNS:
  clean,n=pattern.subn("[REDACTED_SECRET]",clean)
  if n: findings.append("SECRET_REDACTED")
 for pattern in PII_PATTERNS:
  clean,n=pattern.subn("[REDACTED_PII]",clean)
  if n: findings.append("PII_REDACTED")
 token=re.compile(r'(?<![A-Za-z0-9])[A-Za-z0-9_+/=-]{32,}(?![A-Za-z0-9])')
 def entropy(value):
  from math import log2
  from collections import Counter
  counts=Counter(value)
  return -sum((count/len(value))*log2(count/len(value)) for count in counts.values())
 def redact(match):
  value=match.group(0)
  if len(set(value))>=12 and entropy(value)>=4.2:
   findings.append("HIGH_ENTROPY_TOKEN_REDACTED")
   return "[REDACTED_HIGH_ENTROPY]"
  return value
 return token.sub(redact,clean),sorted(set(findings))
def restricted_url(value):
 if not value: return False
 try:
  parsed=urlparse(value)
  if parsed.scheme not in {"http","https"} or not parsed.hostname: return True
  host=parsed.hostname.lower().rstrip(".")
  if host in BLOCKED_HOSTS or any(host.endswith("."+blocked) for blocked in BLOCKED_HOSTS) or host=="localhost" or host.endswith(".local"): return True
  try:
   if not ipaddress.ip_address(host).is_global: return True
  except ValueError: pass
  return False
 except ValueError: return True
def main():
 args=parser("DreamCo Stage 1 policy gate").parse_args()
 too_large=Path(args.input).stat().st_size>MAX_INPUT_BYTES
 raw={} if too_large else read_json(args.input)
 if not isinstance(raw,dict): raw={}
 text=raw.get("content",""); permission=raw.get("permission",{})
 if not isinstance(permission,dict): permission={}
 code="RAW_UPLOAD_TOO_LARGE" if too_large else "ACCEPTED"; findings=[]
 if code=="ACCEPTED":
  if not isinstance(text,str): code="INVALID_CONTENT"; text=""
  elif len(text.encode("utf-8"))>MAX_BYTES: code="FILE_TOO_LARGE"
  elif permission.get("authorized") is not True: code="PERMISSION_REQUIRED"
  elif permission.get("target_kind") not in {"user_owned","public_api","open_source","user_authorized_logs","user_authorized_workflow","user_authorized_schema"}: code="TARGET_NOT_ALLOWED"
  elif permission.get("bypass_requested") or permission.get("drm_circumvention") or permission.get("unauthorized_login_scraping"): code="PROHIBITED_ACCESS"
  elif permission.get("target_kind")=="open_source" and permission.get("license_id") not in {"MIT","Apache-2.0","BSD-2-Clause","BSD-3-Clause","ISC","0BSD"}: code="LICENSE_REVIEW_REQUIRED"
  elif raw.get("source_url") and (not isinstance(raw.get("source_url"),str) or restricted_url(raw.get("source_url"))): code="RESTRICTED_DOMAIN"
 archive=raw.get("archive_base64")
 if code=="ACCEPTED" and archive:
  try:
   if not isinstance(archive,str) or len(archive)>MAX_ARCHIVE_ENCODED: raise ValueError("archive encoded size limit")
   data=base64.b64decode(archive,validate=True)
   with zipfile.ZipFile(io.BytesIO(data)) as archive_file:
    infos=archive_file.infolist()
    if len(infos)>MAX_ZIP_FILES or sum(item.file_size for item in infos)>MAX_EXPANDED or any(item.file_size/max(item.compress_size,1)>MAX_RATIO for item in infos):
     code="ARCHIVE_LIMIT_EXCEEDED"
  except Exception: code="INVALID_OR_UNSAFE_ARCHIVE"
 clean,redactions=scan(text) if code=="ACCEPTED" else ("",[])
 findings.extend(redactions)
 job_id=raw.get("job_id")
 if not isinstance(job_id,str) or not job_id.strip(): job_id=str(uuid.uuid4())
 artifact_type=raw.get("artifact_type","auto")
 if not isinstance(artifact_type,str): artifact_type="auto"
 result={"schema_version":"dreamco.artifact_manifest.v1","job_id":job_id,"status":"ACCEPTED" if code=="ACCEPTED" else "REJECTED","artifact_type":artifact_type,"sha256":digest(clean),"sanitized_text":clean,"policy":{"decision":"PASS" if code=="ACCEPTED" else "BLOCK","audit_code":code,"findings":findings}}
 validate(result,"artifact_manifest.schema.json"); write_json(args.output,result)
 if code!="ACCEPTED": sys.exit(2)
if __name__=="__main__": main()
