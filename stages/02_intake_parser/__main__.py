import ast,csv,io,json,re
from urllib.parse import urlsplit
from ..common import parser,read_json,write_json,validate

def sanitize_har_path(value):
 path=urlsplit(str(value or "")).path
 safe=[]
 for segment in path.split("/"):
  if (re.fullmatch(r"\d+",segment)
      or re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}",segment)
      or "@" in segment
      or re.fullmatch(r"[A-Za-z0-9_-]{32,}",segment)):
   safe.append("{id}")
  else:
   safe.append(segment)
 return "/".join(safe)

def safe_media_type(value):
 value=str(value or "").split(";",1)[0].strip().lower()
 pattern=r"[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+"
 return value if re.fullmatch(pattern,value) else "unspecified"
def parse(text,kind):
 if kind in {"python","python_source"}:
  tree=ast.parse(text)
  return {"language":"python","functions":[{"arity":len(node.args.args),"async":isinstance(node,ast.AsyncFunctionDef)} for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))],"control_flow":[type(node).__name__ for node in ast.walk(tree) if isinstance(node,(ast.If,ast.For,ast.While,ast.Try,ast.Match))],"imports":sorted({node.module or "" for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)}|{alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names})}
 if kind in {"json","openapi_json","har"}:
  data=json.loads(text)
  if kind=="har":
   endpoints=[]
   for entry in data.get("log",{}).get("entries",[]):
    request=entry.get("request",{}); response=entry.get("response",{})
    request_headers={str(h.get("name","")).lower():h.get("value") for h in request.get("headers",[])}
    response_names=sorted({str(h.get("name","")).lower() for h in response.get("headers",[])})
    endpoints.append({"method":request.get("method",""),"path":sanitize_har_path(request.get("url","")),"status":response.get("status"),"request_content_type":safe_media_type(request_headers.get("content-type","")),"request_body_present":bool(request.get("postData")),"request_body_size":len(str(request.get("postData",{}).get("text",""))) if isinstance(request.get("postData"),dict) else 0,"response_header_names":[name for name in response_names if "rate" in name or name=="retry-after"],"response_content_type":safe_media_type(next((h.get("value","") for h in response.get("headers",[]) if str(h.get("name","")).lower()=="content-type"),""))})
   return {"endpoints":endpoints}
  if kind=="openapi_json":
   endpoints=[]
   for path,methods in sorted(data.get("paths",{}).items()):
    for method,operation in sorted(methods.items()):
     if method.lower() not in {"get","post","put","patch","delete","head","options"}: continue
     body=operation.get("requestBody",{}).get("content",{})
     response=operation.get("responses",{})
     rate_keys=sorted(key for key in operation if key.lower().startswith(("x-ratelimit","x-rate-limit")))
     endpoints.append({"method":method.upper(),"path":path,"parameter_count":len(operation.get("parameters",[])),"request_content_types":sorted(body),"request_schema_type":next((v.get("schema",{}).get("type","unspecified") for v in body.values()),"none"),"request_property_count":len(next((v.get("schema",{}).get("properties",{}) for v in body.values()),{})),"response_codes":sorted(response),"response_content_types":sorted({ct for response_item in response.values() for ct in response_item.get("content",{})}),"rate_limit_extensions":rate_keys,"auth_required":bool(operation.get("security",data.get("security",[])))})
   return {"endpoints":endpoints}
  if isinstance(data,list):
   keys=sorted({key for row in data if isinstance(row,dict) for key in row})
   return {"row_count":len(data),"columns":[{"name":"field_"+str(index+1),"present_count":sum(key in row for row in data if isinstance(row,dict))} for index,key in enumerate(keys)]}
  return {"json_type":type(data).__name__,"top_level_keys":len(data) if isinstance(data,dict) else 0}
 if kind=="csv":
  rows=list(csv.DictReader(io.StringIO(text))); names=list(rows[0].keys()) if rows else []; columns=[]
  for index,name in enumerate(names):
   values=[row.get(name,"") for row in rows]
   types={"integer" if value.isdigit() else "string" for value in values if value not in ("",None)}
   columns.append({"name":"field_"+str(index+1),"inferred_types":sorted(types),"null_count":sum(value in ("",None) for value in values),"unique_count":len(set(value for value in values if value not in ("",None))),"candidate_primary_key":bool(values) and len(set(values))==len(values) and all(value not in ("",None) for value in values)})
  return {"row_count":len(rows),"columns":columns}
 if kind in {"javascript_source","typescript_source","java_source","go_source","rust_source"}:
  language={"javascript_source":"javascript","typescript_source":"typescript","java_source":"java","go_source":"go","rust_source":"rust"}[kind]
  from reverse_engineer.parsers.treesitter import parse_tree_sitter
  parsed=parse_tree_sitter(text,language); facts=parsed["facts"]
  return {"language":language,"functions":[{"arity":function.get("parameter_node_count") or 0} for function in facts.get("functions",[])],"control_flow":[item.get("control_constructs",[]) for item in facts.get("control_flow",[])],"imports":facts.get("dependencies",[])}
 raise ValueError("Unsupported artifact type; parser fails closed.")

def main():
 args=parser("DreamCo Stage 2 deterministic parser").parse_args()
 manifest=read_json(args.input); validate(manifest,"artifact_manifest.schema.json")
 if manifest.get("status")!="ACCEPTED" or manifest.get("policy",{}).get("decision")!="PASS": raise PermissionError("Manifest is not accepted.")
 kind=manifest.get("artifact_type","auto")
 if kind=="auto":
  try:
   obj=json.loads(manifest["sanitized_text"])
   kind="har" if "log" in obj and "entries" in obj.get("log",{}) else ("openapi_json" if "openapi" in obj else "json")
  except Exception:
   lines=manifest["sanitized_text"].splitlines()
   kind="python" if "def " in manifest["sanitized_text"] else "csv" if lines and "," in lines[0] else "unknown"
 facts=parse(manifest["sanitized_text"],kind)
 result={"schema_version":"dreamco.parsed_facts.v1","job_id":manifest["job_id"],"artifact_type":"code" if kind in {"python","python_source","javascript_source","typescript_source","java_source","go_source","rust_source"} else "api" if kind in {"openapi_json","har"} else "data","source_sha256":manifest["sha256"],"facts":facts,"warnings":["Static parsing only; no user code was imported or executed. Header values, query values and request/response bodies are not retained."]}
 validate(result,"parsed_facts.schema.json"); write_json(args.output,result)
if __name__=="__main__": main()
