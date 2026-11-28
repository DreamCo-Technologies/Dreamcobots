import ast,csv,io,json
from urllib.parse import urlsplit
from ..common import parser,read_json,write_json,validate
def parse(text,kind):
 if kind in {"python","python_source"}:
  tree=ast.parse(text)
  return {"language":"python","functions":[{"arity":len(node.args.args),"async":isinstance(node,ast.AsyncFunctionDef)} for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))],"control_flow":[type(node).__name__ for node in ast.walk(tree) if isinstance(node,(ast.If,ast.For,ast.While,ast.Try,ast.Match))],"imports":sorted({node.module or "" for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)}|{alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names})}
 if kind in {"json","openapi_json","har"}:
  data=json.loads(text)
  if kind=="har":
   entries=data.get("log",{}).get("entries",[])
   return {"endpoints":[{"method":entry.get("request",{}).get("method",""),"path":urlsplit(entry.get("request",{}).get("url","")).path,"status":entry.get("response",{}).get("status")} for entry in entries]}
  if kind=="openapi_json":
   paths=data.get("paths",{})
   return {"endpoints":[{"method":method.upper(),"path":path} for path,methods in sorted(paths.items()) for method in sorted(methods) if method.lower() in {"get","post","put","patch","delete","head","options"}]}
  if isinstance(data,list):
   keys=sorted({key for row in data if isinstance(row,dict) for key in row})
   return {"row_count":len(data),"columns":[{"name":"field_"+str(index+1),"present_count":sum(key in row for row in data if isinstance(row,dict))} for index,key in enumerate(keys)]}
  return {"json_type":type(data).__name__,"top_level_keys":len(data) if isinstance(data,dict) else 0}
 if kind=="csv":
  rows=list(csv.DictReader(io.StringIO(text)))
  names=list(rows[0].keys()) if rows else []
  columns=[]
  for index,name in enumerate(names):
   values=[row.get(name,"") for row in rows]
   types={"integer" if value.isdigit() else "string" for value in values if value not in ("",None)}
   columns.append({"name":"field_"+str(index+1),"inferred_types":sorted(types),"null_count":sum(value in ("",None) for value in values)})
  return {"row_count":len(rows),"columns":columns}
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
 result={"schema_version":"dreamco.parsed_facts.v1","job_id":manifest["job_id"],"artifact_type":"code" if kind in {"python","python_source"} else "api" if kind in {"openapi_json","har"} else "data","source_sha256":manifest["sha256"],"facts":facts,"warnings":["Static parsing only; no user code was imported or executed."]}
 validate(result,"parsed_facts.schema.json"); write_json(args.output,result)
if __name__=="__main__": main()
