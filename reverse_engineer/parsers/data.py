"""CSV/JSON schema inference; never emits data row values."""
import csv,io,json
from collections import Counter
def kind(v):
    v=str(v).strip()
    if not v:return "null"
    if v.lower() in {"true","false"}:return "boolean"
    try:int(v);return "integer"
    except ValueError:pass
    try:float(v);return "number"
    except ValueError:return "string"
def column(name,values):
    counts=Counter(kind(v) for v in values); nonnull=sum(n for k,n in counts.items() if k!="null")
    return {"name":name,"inferred_types":sorted(k for k,n in counts.items() if k!="null") or ["unknown"],"null_count":counts.get("null",0),"non_null_count":nonnull,"unique_count":len(set(v for v in values if str(v).strip()))}
def parse_csv(content):
    reader=csv.DictReader(io.StringIO(content));
    if not reader.fieldnames:raise ValueError("CSV header row required")
    rows=list(reader); cols=[column(n,[r.get(n,"") or "" for r in rows]) for n in reader.fieldnames]
    keys=[c["name"] for c in cols if c["non_null_count"]==len(rows) and c["unique_count"]==len(rows)]
    return {"artifact_type":"data","facts":{"format":"csv","row_count":len(rows),"columns":cols,"candidate_keys":keys,"source_values_retained":False},"warnings":["Candidate keys are heuristic; foreign keys and business meaning require owner confirmation."]}
def parse_json_data(content):
    value=json.loads(content); rows=value if isinstance(value,list) else [value]
    if not rows or not all(isinstance(r,dict) for r in rows):return {"artifact_type":"data","facts":{"format":"json","top_level_type":type(value).__name__,"source_values_retained":False},"warnings":["Nested or non-record JSON requires domain-specific schema review."]}
    names=sorted(set().union(*(r.keys() for r in rows))); cols=[column(str(n),["" if r.get(n) is None else str(r.get(n)) for r in rows]) for n in names]
    return {"artifact_type":"data","facts":{"format":"json","row_count":len(rows),"columns":cols,"source_values_retained":False},"warnings":["Type inference does not establish primary or foreign keys."]}
