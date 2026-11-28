import ast,csv,io,json,sys
from urllib.parse import urlsplit
from ..common import parser,read_json,write_json,digest,validate

def parse(text,kind):
    if kind in {"python","python_source"}:
        tree=ast.parse(text)
        return {"language":"python","functions":[{"arity":len(n.args.args),"async":isinstance(n,ast.AsyncFunctionDef)} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))],"control_flow":[type(n).__name__ for n in ast.walk(tree) if isinstance(n,(ast.If,ast.For,ast.While,ast.Try,ast.Match))],"imports":sorted({n.module or "" for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}|{a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names})}
    if kind in {"json","openapi_json","har"}:
        data=json.loads(text)
        if kind=="har":
            entries=data.get("log",{}).get("entries",[])
            return {"endpoints":[{"method":e.get("request",{}).get("method",""),"path":urlsplit(e.get("request",{}).get("url","")).path,"status":e.get("response",{}).get("status")} for e in entries]}
        if kind=="openapi_json":
            paths=data.get("paths",{})
            return {"endpoints":[{"method":m.upper(),"path":p} for p,methods in sorted(paths.items()) for m in sorted(methods) if m.lower() in {"get","post","put","patch","delete","head","options"}]}
        if isinstance(data,list):
            keys=sorted({k for row in data if isinstance(row,dict) for k in row})
            return {"row_count":len(data),"columns":[{"name":"field_"+str(i+1),"present_count":sum(k in row for row in data if isinstance(row,dict))} for i,k in enumerate(keys)]}
        return {"json_type":type(data).__name__,"top_level_keys":len(data) if isinstance(data,dict) else 0}
    if kind=="csv":
        rows=list(csv.DictReader(io.StringIO(text)))
        names=list(rows[0].keys()) if rows else []
        cols=[]
        for i,k in enumerate(names):
            vals=[r.get(k,"") for r in rows]; types={"integer" if v.isdigit() else "string" for v in vals if v not in ("",None)}
            cols.append({"name":"field_"+str(i+1),"inferred_types":sorted(types),"null_count":sum(v in ("",None) for v in vals)})
        return {"row_count":len(rows),"columns":cols}
    raise ValueError("Unsupported artifact type; parser fails closed.")
def main():
    a=parser("DreamCo Stage 2 deterministic parser").parse_args(); manifest=read_json(a.input)
    if manifest.get("status")!="ACCEPTED" or manifest.get("policy",{}).get("decision")!="PASS": raise PermissionError("Manifest is not accepted.")
    kind=manifest.get("artifact_type","auto")
    if kind=="auto":
        try:
            obj=json.loads(manifest["sanitized_text"]); kind="har" if "log" in obj and "entries" in obj.get("log",{}) else ("openapi_json" if "openapi" in obj else "json")
        except Exception: kind="python" if "def " in manifest["sanitized_text"] else "csv" if "," in manifest["sanitized_text"].splitlines()[0] else "unknown"
    facts=parse(manifest["sanitized_text"],kind)
    result={"schema_version":"dreamco.parsed_facts.v1","job_id":manifest["job_id"],"artifact_type":"code" if kind in {"python","python_source"} else "api" if kind in {"openapi_json","har"} else "data","source_sha256":manifest["sha256"],"facts":facts,"warnings":["Static parsing only; no user code was imported or executed."]}
    validate(result,"parsed_facts.schema.json"); write_json(a.output,result)
if __name__=="__main__":main()
