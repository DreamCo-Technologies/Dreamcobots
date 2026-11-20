"""Metadata-only public source discovery. Network is opt-in; no dataset files are downloaded."""
from __future__ import annotations
import json
import os
import re
import urllib.parse
import urllib.request
from typing import Any

class SourceAccessError(RuntimeError):
    pass

def _get_json(url: str, timeout: int = 12) -> Any:
    if os.environ.get("DREAMCO_ALLOW_SOURCE_NETWORK") != "1":
        raise SourceAccessError("Set DREAMCO_ALLOW_SOURCE_NETWORK=1 for explicit metadata discovery")
    headers = {"User-Agent": "DreamCo-Buddy-DatasetDiscovery/1.0", "Accept": "application/json"}
    token = os.environ.get("GITHUB_TOKEN")
    if "api.github.com" in url and token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise SourceAccessError(f"Unexpected HTTP status {response.status}")
            return json.loads(response.read(2_000_000).decode("utf-8"))
    except Exception as exc:
        raise SourceAccessError(f"Metadata discovery failed: {type(exc).__name__}") from exc

def search_huggingface(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"search": query, "limit": max(1, min(limit, 30))}, safe="/")
    data = _get_json("https://huggingface.co/api/datasets?" + params)
    return [{"source": "huggingface", "id": x.get("id"), "url": "https://huggingface.co/datasets/" + str(x.get("id")), "last_modified": x.get("lastModified"), "downloads": x.get("downloads"), "likes": x.get("likes"), "tags": x.get("tags", []), "license": next((t.split(":",1)[1] for t in x.get("tags",[]) if str(t).startswith("license:")), None), "rights_status": "UNVERIFIED_REQUIRES_DATASET_CARD_REVIEW"} for x in data if x.get("id")]

def search_openml(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "limit": max(1, min(limit, 30))})
    data = _get_json("https://www.openml.org/api/v1/json/data/list?" + params)
    rows = data.get("data", {}).get("dataset", [])
    if isinstance(rows, dict): rows = [rows]
    return [{"source": "openml", "id": str(x.get("did")), "name": x.get("name"), "url": f"https://www.openml.org/d/{x.get('did')}", "license": x.get("licence"), "rights_status": "UNVERIFIED_REQUIRES_TERMS_REVIEW"} for x in rows if x.get("did")]

def search_uci(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"search": query, "skip": 0, "take": max(1, min(limit, 30))})
    data = _get_json("https://archive.ics.uci.edu/api/datasets?" + params)
    rows = data.get("data", data if isinstance(data, list) else [])
    found = []
    for x in rows if isinstance(rows, list) else []:
        rid = x.get("ID") or x.get("id")
        if not rid:
            continue
        link = str(x.get("Link") or x.get("url") or f"https://archive.ics.uci.edu/dataset/{rid}")
        if link.startswith("http://"):
            link = "https://" + link[len("http://"):]
        if not link.startswith("https://"):
            link = f"https://archive.ics.uci.edu/dataset/{rid}"
        found.append({"source":"uci","id":str(rid),"name":x.get("Name") or x.get("name"),
            "url":link,"license":x.get("License") or x.get("license"),
            "rights_status":"UNVERIFIED_REQUIRES_TERMS_REVIEW"})
    return found

def search_github(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"q": query + " in:name,description", "per_page": max(1, min(limit, 30))})
    data = _get_json("https://api.github.com/search/repositories?" + params)
    return [{"source": "github", "id": x.get("full_name"), "name": x.get("name"), "url": x.get("html_url"), "license": (x.get("license") or {}).get("spdx_id"), "default_branch": x.get("default_branch"), "rights_status": "UNVERIFIED_REQUIRES_LICENSE_AND_CONTENT_REVIEW"} for x in data.get("items", [])]


def search_zenodo(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "size": max(1, min(limit, 30))})
    data = _get_json("https://zenodo.org/api/records?" + params)
    rows = data.get("hits", {}).get("hits", [])
    found = []
    for item in rows:
        meta = item.get("metadata", {})
        license_meta = meta.get("license") or {}
        license_id = license_meta.get("id") if isinstance(license_meta, dict) else str(license_meta or "")
        rid = str(item.get("id") or "")
        if rid:
            found.append({"source":"zenodo","id":rid,"name":meta.get("title"),
                "url":item.get("links",{}).get("self_html") or f"https://zenodo.org/records/{rid}",
                "license":license_id,"version":meta.get("version"),"publication_date":meta.get("publication_date"),
                "rights_status":"UNVERIFIED_REQUIRES_RECORD_AND_FILE_LICENSE_REVIEW"})
    return found

def search_datagov(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "rows": max(1, min(limit, 30))})
    data = _get_json("https://catalog.data.gov/api/3/action/package_search?" + params)
    rows = data.get("result", {}).get("results", [])
    return [{"source":"data_gov","id":str(x.get("id") or x.get("name")),
        "name":x.get("title"),"url":f"https://catalog.data.gov/dataset/{x.get('name')}",
        "license":x.get("license_title") or x.get("license_id"),
        "organization":(x.get("organization") or {}).get("title"),
        "rights_status":"UNVERIFIED_REQUIRES_RESOURCE_LEVEL_LICENSE_REVIEW"} for x in rows if x.get("id") or x.get("name")]

def search_kaggle(query: str, limit: int = 10) -> list[dict]:
    username, key = os.environ.get("KAGGLE_USERNAME"), os.environ.get("KAGGLE_KEY")
    if not username or not key:
        raise SourceAccessError("Kaggle discovery requires operator-provided KAGGLE_USERNAME and KAGGLE_KEY")
    params = urllib.parse.urlencode({"search":query,"page":1,"pageSize":max(1,min(limit,30))})
    request = urllib.request.Request("https://www.kaggle.com/api/v1/datasets/list?"+params,
        headers={"User-Agent":"DreamCo-Buddy-DatasetDiscovery/1.0","Authorization":"Basic "+
            __import__("base64").b64encode(f"{username}:{key}".encode()).decode()},method="GET")
    try:
        with urllib.request.urlopen(request,timeout=12) as response:
            data=json.loads(response.read(2_000_000).decode("utf-8"))
    except Exception as exc:
        raise SourceAccessError(f"Kaggle metadata discovery failed: {type(exc).__name__}") from exc
    return [{"source":"kaggle","id":str(x.get("ref") or x.get("id")),
        "name":x.get("title"),"url":"https://www.kaggle.com/datasets/"+str(x.get("ref") or ""),
        "license":x.get("licenseName"),"last_updated":x.get("lastUpdated"),
        "rights_status":"UNVERIFIED_REQUIRES_DATASET_TERMS_AND_FILE_REVIEW"} for x in data if x.get("ref") or x.get("id")]

def inspect_huggingface_dataset_card(dataset_id: str) -> dict:
    if not dataset_id or "/" not in dataset_id:
        raise ValueError("A fully qualified Hugging Face dataset ID is required")
    url="https://huggingface.co/datasets/"+urllib.parse.quote(dataset_id,safe="/")+"/raw/main/README.md"
    request=urllib.request.Request(url,headers={"User-Agent":"DreamCo-Buddy-DatasetDiscovery/1.0"},method="GET")
    if os.environ.get("DREAMCO_ALLOW_SOURCE_NETWORK")!="1":
        raise SourceAccessError("Set DREAMCO_ALLOW_SOURCE_NETWORK=1 for dataset-card inspection")
    try:
        with urllib.request.urlopen(request,timeout=12) as response:
            raw=response.read(1_000_000)
            text=raw.decode("utf-8")
    except Exception as exc:
        raise SourceAccessError(f"Dataset-card inspection failed: {type(exc).__name__}") from exc
    import hashlib
    front={}
    if text.startswith("---"):
        parts=text.split("---",2)
        if len(parts)>2:
            for line in parts[1].splitlines():
                if ":" in line and not line.lstrip().startswith("#"):
                    key,value=line.split(":",1);front[key.strip().lower()]=value.strip().strip('"\\'')
    return {"source":"huggingface_dataset_card","id":dataset_id,
        "url":"https://huggingface.co/datasets/"+dataset_id,
        "card_sha256":hashlib.sha256(raw).hexdigest(),"card_bytes":len(raw),
        "license":front.get("license"),"tags":front.get("tags"),
        "task_categories":front.get("task_categories"),"language":front.get("language"),
        "card_front_matter":front,"ai_training_allowed":front.get("ai_training_allowed"),"rights_status":"UNVERIFIED_REQUIRES_FULL_CARD_CONTENT_AND_LICENSE_REVIEW",
        "raw_card_persisted":False}

def discover(query: str, limit: int = 8, include_kaggle: bool = True) -> dict:
    if len((query or "").strip()) < 2:
        raise ValueError("A meaningful search query is required")
    results, errors = [], {}
    for name, fn in (("huggingface", search_huggingface), ("openml", search_openml), ("uci", search_uci), ("github", search_github), ("zenodo", search_zenodo), ("data_gov", search_datagov)) + ((("kaggle", search_kaggle),) if include_kaggle else ()):
        try:
            results.extend(fn(query, limit))
        except SourceAccessError as exc:
            errors[name] = str(exc)
    models = []
    try:
        models = search_huggingface_models(query, limit)
    except SourceAccessError as exc:
        errors["huggingface_models"] = str(exc)
    return {"query": query, "results": results, "model_results": models, "source_errors": errors, "downloaded_files": False, "training_approved": False}

def search_huggingface_models(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"search": query, "limit": max(1, min(limit, 30))}, safe="/")
    data = _get_json("https://huggingface.co/api/models?" + params)
    return [{"source": "huggingface_model", "id": x.get("id"), "url": "https://huggingface.co/" + str(x.get("id")), "last_modified": x.get("lastModified"), "downloads": x.get("downloads"), "likes": x.get("likes"), "pipeline_tag": x.get("pipeline_tag"), "tags": x.get("tags", []), "license": next((t.split(":",1)[1] for t in x.get("tags",[]) if str(t).startswith("license:")), None), "rights_status": "UNVERIFIED_REQUIRES_MODEL_CARD_AND_LICENSE_REVIEW"} for x in data if x.get("id")]

def fetch_authorized_github_file(owner: str, repo: str, path: str, revision: str = "HEAD") -> dict:
    """Read one file from a repository visible to the supplied GitHub token; never persist it."""
    token = os.environ.get("GITHUB_TOKEN")
    if os.environ.get("DREAMCO_ALLOW_SOURCE_NETWORK") != "1" or not token:
        raise SourceAccessError("Explicit source-network opt-in and GITHUB_TOKEN are required")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", owner) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", repo):
        raise ValueError("GitHub owner and repository names are invalid")
    if not path or any(part in {".", ".."} for part in path.split("/")) or not revision:
        raise ValueError("GitHub file path and revision must be explicit and traversal-free")
    encoded_path = urllib.parse.quote(path, safe="/")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}?ref=" + urllib.parse.quote(revision, safe="")
    data = _get_json(url)
    import base64
    if data.get("type") != "file" or not data.get("content") or int(data.get("size") or 0) > 1_000_000:
        raise SourceAccessError("The selected GitHub path is not a readable text file within the 1 MB limit")
    try:
        content = base64.b64decode(data["content"]).decode("utf-8")
    except Exception as exc:
        raise SourceAccessError("The selected GitHub file is not UTF-8 text") from exc
    return {"source": "authorized_github_file", "repository": f"{owner}/{repo}", "path": path,
            "revision": revision, "blob_sha": data.get("sha"), "size": data.get("size"),
            "downloaded_to_memory_only": True, "persisted": False, "content": content}

