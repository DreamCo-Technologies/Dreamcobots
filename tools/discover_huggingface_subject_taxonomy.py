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
                        metadata_keys = {"id", "label", "name", "tag", "task", "pipeline_tag", "category", "description", "type"}
                        for k,v in x.items():
                            if isinstance(k,str) and k.lower() not in metadata_keys: found.append(k)
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
    space_method=getattr(api,"get_space_tags",None)
    space=plain(space_method()) if callable(space_method) else None
    allowed={"pipeline_tags","tasks","task","pipeline_tag","task_categories","task_ids","tags","tag","categories","category"}
    model_terms=values_under(model,allowed)
    dataset_terms=values_under(dataset,allowed)
    space_terms=values_under(space,allowed) if space is not None else []
    normalize=lambda values: sorted({x.strip().lower().replace(" ","-").replace("_","-") for x in values if len(x.strip())>1})
    model_subjects=normalize(model_terms)
    dataset_subjects=normalize(dataset_terms)
    space_subjects=normalize(space_terms)
    terms=sorted(set(model_subjects+dataset_subjects+space_subjects))
    if not terms: raise SystemExit("Hub taxonomy response did not expose recognized task categories; refusing empty refresh.")
    result={"schema":"dreamco.huggingface_subject_taxonomy.v1","source":"Hugging Face Hub HfApi.get_model_tags/get_dataset_tags",
      "model_tag_taxonomy":model,"dataset_tag_taxonomy":dataset,"space_tag_taxonomy":space,
      "subject_terms":terms,"subject_terms_by_artifact_type":{"models":model_subjects,"datasets":dataset_subjects,"spaces":space_subjects},
      "counts":{"subject_terms":len(terms),"model_subject_terms":len(model_subjects),"dataset_subject_terms":len(dataset_subjects),"space_subject_terms":len(space_subjects)},
      "capabilities":{"models":True,"datasets":True,"spaces":space is not None},
      "status":"refreshed_from_live_hub_taxonomy" if space is not None else "refreshed_models_and_datasets_spaces_taxonomy_unavailable",
      "coverage_note":"These are current task/tag categories, not every repository or every possible subject. Discovery inventory must report pagination and coverage separately."}
    path=Path(a.out); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["counts"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
