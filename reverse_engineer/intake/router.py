"""Deterministic intake detection. This module never fetches URLs."""
import json
from pathlib import PurePosixPath
EXTENSIONS={".py":"python_source",".js":"javascript_source",".ts":"typescript_source",".tsx":"typescript_source",".java":"java_source",".go":"go_source",".rs":"rust_source",".cpp":"cpp_source",".cxx":"cpp_source",".cc":"cpp_source",".hpp":"cpp_source",".hxx":"cpp_source",".hh":"cpp_source",".cu":"cuda_source",".cuda":"cuda_source",".cuh":"cuda_source",".json":"json",".csv":"csv",".har":"har",".yaml":"openapi_yaml",".yml":"openapi_yaml"}
def detect_artifact(filename, content):
    suffix=PurePosixPath(filename).suffix.lower()
    if suffix in EXTENSIONS: return EXTENSIONS[suffix]
    try: value=json.loads(content)
    except (ValueError,TypeError): return "unknown"
    if isinstance(value,dict) and ("openapi" in value or "swagger" in value): return "openapi_json"
    if isinstance(value,dict) and "log" in value and "entries" in value: return "har"
    return "json"
def route_artifact(filename, content, permission=None):
    return {"artifact_type":detect_artifact(filename,content),"filename":PurePosixPath(filename).name,"content":content,"permission":permission or {}}
