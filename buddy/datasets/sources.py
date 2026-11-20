"""Metadata-only public source discovery. Network is opt-in; no dataset files are downloaded."""
from __future__ import annotations
import json
import os
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
    return [{"source": "uci", "id": str(x.get("ID") or x.get("id")), "name": x.get("Name") or x.get("name"), "url": x.get("Link") or x.get("url"), "license": x.get("License") or x.get("license"), "rights_status": "UNVERIFIED_REQUIRES_TERMS_REVIEW"} for x in rows if x.get("ID") or x.get("id")]

def search_github(query: str, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"q": query + " in:name,description", "per_page": max(1, min(limit, 30))})
    data = _get_json("https://api.github.com/search/repositories?" + params)
    return [{"source": "github", "id": x.get("full_name"), "name": x.get("name"), "url": x.get("html_url"), "license": (x.get("license") or {}).get("spdx_id"), "default_branch": x.get("default_branch"), "rights_status": "UNVERIFIED_REQUIRES_LICENSE_AND_CONTENT_REVIEW"} for x in data.get("items", [])]

def discover(query: str, limit: int = 8) -> dict:
    if len((query or "").strip()) < 2:
        raise ValueError("A meaningful search query is required")
    results, errors = [], {}
    for name, fn in (("huggingface", search_huggingface), ("openml", search_openml), ("uci", search_uci), ("github", search_github)):
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
    parts = [owner, repo, path, revision]
    if any(not x or x in {".", ".."} for x in parts):
        raise ValueError("Owner, repository, path, and revision must be explicit")
    encoded_path = urllib.parse.quote(path, safe="/")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}?ref=" + urllib.parse.quote(revision, safe="")
    data = _get_json(url)
    import base64
    if data.get("type") != "file" or not data.get("content"):
        raise SourceAccessError("The selected GitHub path is not a readable text file")
    try:
        content = base64.b64decode(data["content"]).decode("utf-8")
    except Exception as exc:
        raise SourceAccessError("The selected GitHub file is not UTF-8 text") from exc
    return {"source": "authorized_github_file", "repository": f"{owner}/{repo}", "path": path,
            "revision": revision, "blob_sha": data.get("sha"), "size": data.get("size"),
            "downloaded_to_memory_only": True, "persisted": False, "content": content}

