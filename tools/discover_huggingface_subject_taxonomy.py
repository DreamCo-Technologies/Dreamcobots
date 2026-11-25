#!/usr/bin/env python3
"""Refresh Hugging Face's official model and dataset task/tag taxonomies."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

def plain(value:Any)->Any:
    if isinstance(value,(str,int,float,bool)) or value is None: return value
    if isinstance(value,dict): return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,set)): return [plain(x) for x in value]
    for method in ("to_dict","dict"):
        fn=getattr(value,method,None)
        if callable(fn):
            try: return plain(fn())
            except Exception: pass
    if hasattr(value,"__dict__"): return {k:plain(v) for k,v in vars(value).items() if not k.startswith("_")}
    return str(value)

def values_under(data:Any,allowed:set[str],path:tuple[str,...]=())->list[str]:
    found=[]
    if isinstance(data,dict):
        for key,value in data.items():
            name=str(key).lower().replace("-","_")
            next_path=path+(name,)
            if name in allowed:
                def leaves(x:Any)->None:
                    if isinstance(x,str):
                        if x.strip(): found.append(x.strip())
                    elif isinstance(x,dict):
                        for k,v in x.items():
                            if isinstance(k,str): found.append(k)
                            leaves(v)
                    elif isinstance(x,(list,tuple)):
                        for v in x: leaves(v)
                leaves(value)
            else: found.extend(values_under(value,allowed,next_path))
    elif isinstance(data,list):
        for item in data: found.extend(values_under(item,allowed,path))
    return found

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--out",required=True); a=p.parse_args()
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise SystemExit("Install huggingface_hub to refresh the official Hub taxonomy.") from exc
    api=HfApi()
    model=plain(api.get_model_tags())
    dataset=plain(api.get_dataset_tags())
    model_terms=values_under(model,{"pipeline_tags","tasks","task","pipeline_tag","task_categories"})
    dataset_terms=values_under(dataset,{"task_categories","task_ids","tasks","task"})
    terms=sorted({x.lower().replace(" ","-") for x in model_terms+dataset_terms if len(x.strip())>1})
    if not terms: raise SystemExit("Hub taxonomy response did not expose recognized task categories; refusing empty refresh.")
    result={"schema":"dreamco.huggingface_subject_taxonomy.v1","source":"Hugging Face Hub HfApi.get_model_tags/get_dataset_tags",
      "model_tag_taxonomy":model,"dataset_tag_taxonomy":dataset,"subject_terms":terms,
      "counts":{"subject_terms":len(terms)},"status":"refreshed_from_live_hub_taxonomy",
      "coverage_note":"These are current task/tag categories, not every repository or every possible subject. Discovery inventory must report pagination and coverage separately."}
    path=Path(a.out); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["counts"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
