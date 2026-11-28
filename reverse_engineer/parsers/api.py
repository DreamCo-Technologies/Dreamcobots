"""OpenAPI JSON and HAR metadata parsers."""
import json
from urllib.parse import urlsplit
def parse_openapi_json(content):
    doc=json.loads(content)
    if not isinstance(doc,dict) or not (doc.get("openapi") or doc.get("swagger")): raise ValueError("Not an OpenAPI JSON document")
    endpoints=[]
    for path,item in (doc.get("paths") or {}).items():
        if not isinstance(item,dict): continue
        for method,op in item.items():
            if method.lower() not in {"get","post","put","patch","delete","options","head","trace"} or not isinstance(op,dict): continue
            endpoints.append({"path":path,"method":method.upper(),"operation_id":op.get("operationId"),"parameters":[{"name":p.get("name"),"in":p.get("in"),"required":bool(p.get("required"))} for p in op.get("parameters",[]) if isinstance(p,dict)],"request_body_present":"requestBody" in op,"response_codes":sorted((op.get("responses") or {}).keys())})
    return {"artifact_type":"api","facts":{"format":"openapi","version":doc.get("openapi") or doc.get("swagger"),"title":(doc.get("info") or {}).get("title","Untitled API"),"endpoints":endpoints,"source_text_retained":False},"warnings":[]}
def parse_har(content):
    doc=json.loads(content); grouped={}
    for entry in doc.get("log",{}).get("entries",[]):
        req=entry.get("request") or {}; resp=entry.get("response") or {}; u=urlsplit(req.get("url",""))
        key=(req.get("method","GET").upper(),u.scheme,u.netloc,u.path)
        row=grouped.setdefault(key,{"method":key[0],"scheme":key[1],"host":key[2],"path":key[3],"status_codes":set(),"observations":0})
        row["status_codes"].add(resp.get("status")); row["observations"]+=1
    endpoints=[]
    for row in grouped.values(): row["status_codes"]=sorted(x for x in row["status_codes"] if isinstance(x,int)); endpoints.append(row)
    return {"artifact_type":"api","facts":{"format":"har","endpoints":endpoints,"source_text_retained":False},"warnings":["HAR headers, cookies, query values, request bodies and response bodies are discarded."]}
