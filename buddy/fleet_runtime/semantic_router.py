"""Deterministic Buddy semantic candidate router for the full DreamCo learning fleet.

This module ranks specialists for review. It does not execute bots, load weights,
grant permissions, or bypass the canonical division/MasterBot routing contract.
"""
from __future__ import annotations
from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
FLEET=ROOT/"config/bots/bot-manifests.generated.json"
BUSINESS=ROOT/"config/dreamco-business-bot-55-roster.json"
MASTERBOTS=ROOT/"config/masterbot-65-registry.json"

def _tokens(value: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9]+",str(value).casefold()) if len(x)>1}

@lru_cache(maxsize=1)
def _catalog() -> list[dict[str,Any]]:
    fleet=json.loads(FLEET.read_text(encoding="utf-8"))
    business=json.loads(BUSINESS.read_text(encoding="utf-8"))
    rows=[]
    for bot in fleet.get("bots",[]):
        rows.append({"bot_id":"FLEET_"+str(bot["slug"]),"name":bot["name"],
            "division":bot.get("division") or bot.get("primary_domain_owner") or "UNASSIGNED_REVIEW",
            "source_kind":"canonical_fleet","terms":[bot.get("category",""),bot.get("engine","")],
            "source_refs":bot.get("sources",[]),"identity_status":"DUPLICATE_REVIEW_REQUIRED" if "duplicate_profile" in bot.get("flags",[]) else "CANONICAL_MANIFEST_ENTRY",
            "route_manifest":bot})
    for bot in business.get("bots",[]):
        rows.append({"bot_id":bot["bot_id"],"name":bot["name"],
            "division":"Business Bot Foundry / "+bot["cluster"],"source_kind":"commercial_business_microbot",
            "terms":bot.get("focus_tags",[]),"source_refs":["config/dreamco-business-bot-55-roster.json"],
            "identity_status":"OWNER_SPECIFIED_COMMERCIAL_BLUEPRINT","route_manifest":None})
    from tools.place_original_bots import parse_category,parse_system
    network=ROOT/"original-bots/autonomous-income-network"
    systems=ROOT/"original-bots/systems"
    legacy=[]
    for path in sorted(network.glob("category-*.md")):
        legacy.extend(parse_category(path))
    for path in sorted(systems.glob("*.md")):
        legacy.append(parse_system(path))
    for item in legacy:
        stable="LEGACY_"+re.sub(r"[^a-z0-9]+","-",item["source"].casefold()).strip("-")+"_"+str(item.get("index",0) or item["slug"])
        rows.append({"bot_id":stable,"name":item["display_name"],"division":item["primary_division"],
            "source_kind":"legacy_original_bot_or_system","terms":[item.get("kind",""),item.get("mission","")],
            "source_refs":[item["source"]],"identity_status":"HISTORICAL_SOURCE_NOT_RUNTIME_VERIFIED",
            "route_manifest":{"division":item["primary_division"],"primary_domain_owner":item["primary_division"]}})
    ids=[x["bot_id"] for x in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError("Semantic router catalog contains duplicate stable bot IDs")
    return rows

def route_candidates(query: str, top_k: int=5) -> dict[str,Any]:
    clean=" ".join((query or "").split())
    if len(clean)<3:
        raise ValueError("Describe the task in at least three characters")
    if isinstance(top_k,bool) or not 1<=top_k<=10:
        raise ValueError("top_k must be an integer from 1 through 10")
    q=_tokens(clean)
    ranked=[]
    for row in _catalog():
        searchable=" ".join([row["name"],row["division"]," ".join(map(str,row.get("terms",[])))])
        words=_tokens(searchable)
        matched=sorted(q & words)
        phrase=1 if clean.casefold() in searchable.casefold() else 0
        if not matched and not phrase:
            continue
        raw=len(matched)+phrase*2
        score=round(min(1.0,raw/max(2,min(len(q),6))),3)
        route=None
        if row.get("route_manifest"):
            from buddy.fleet_runtime.routing import resolve_route
            route=resolve_route(row["route_manifest"])
        ranked.append({"bot_id":row["bot_id"],"name":row["name"],"division":row["division"],
            "source_kind":row["source_kind"],"matched_terms":matched,"match_score":score,
            "identity_status":row["identity_status"],"source_refs":row.get("source_refs",[]),
            "masterbot_route":route,"execution_authorized":False,"weights_loaded":False})
    ranked.sort(key=lambda x:(-x["match_score"],x["source_kind"]!="commercial_business_microbot",x["name"].casefold(),x["bot_id"]))
    return {"schema":"dreamco.buddy_semantic_candidate_route.v1","query":clean,
        "candidates":ranked[:top_k],"candidate_count":len(ranked),
        "router":"Buddy Semantic Router / Provost","routing_mode":"deterministic_metadata_candidate_ranking",
        "execution_started":False,"weights_loaded":False,"permissions_granted":False,
        "next_step":"Validate primary division ownership, source rights, tool permissions and sandbox readiness before dispatch.",
        "truth_boundary":"A ranked candidate is not proof of capability, trained weights, owner approval, runtime availability or authorization."}
