#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
CONFIG = ROOT / "config" / "division-strengthening-placement-program.json"
OUT_JSON = ROOT / "config" / "generated" / "bot-division-placement-audit.json"
OUT_MD = ROOT / "reports" / "BOT_DIVISION_PLACEMENT_AUDIT.md"

DIVISIONS = [
    "CommandCore","DreamAIInfra","DreamAdmin","DreamAgents","DreamAgriculture","DreamArts","DreamAutomation","DreamBizLaunch","DreamCodeLab","DreamConstruction","DreamContent","DreamCrypto","DreamCustIntel","DreamCyber","DreamData","DreamDecision","DreamEducation","DreamEmpire","DreamEntFinance","DreamFinance","DreamFlow","DreamFood","DreamGlobal","DreamHealth","DreamInfluence","DreamLegal","DreamLoans","DreamMaintenance","DreamMarket","DreamMilitary","DreamOps","DreamPayments","DreamPersonalCare","DreamPlanetary","DreamProServices","DreamProduction","DreamProtection","DreamRealEstate","DreamRetail","DreamSalesPro","DreamScience","DreamSocial","DreamTrade","DreamTransport","GameTitan"
]

KEYWORDS: dict[str, set[str]] = {
    "CommandCore": {"orchestration","router","routing","command","approval","memory","governance","control tower","system health","kill switch"},
    "DreamAIInfra": {"model","inference","embedding","vector","gpu","compute","llm","ai infrastructure","observability","serving","quantization"},
    "DreamAdmin": {"calendar","meeting","email","document","records","office","assistant","administrative","scheduling","forms"},
    "DreamAgents": {"agent","multi-agent","tool calling","agentic","worker","agent framework","agent evaluation"},
    "DreamAgriculture": {"farm","crop","soil","livestock","agriculture","agricultural","irrigation","harvest","grower"},
    "DreamArts": {"art","artist","gallery","painting","illustration","performance art","portfolio","sculpture","creative direction"},
    "DreamAutomation": {"automation","workflow","trigger","webhook","integration","zap","event-driven","scheduler","retry","orchestration"},
    "DreamBizLaunch": {"startup","business launch","founder","business model","company formation","entrepreneur","go-to-market","offer design"},
    "DreamCodeLab": {"code","coding","developer","software","debug","programming","compiler","repository","git","test","deploy","api engineering"},
    "DreamConstruction": {"construction","contractor","estimate","jobsite","permit","building","carpentry","blueprint","project schedule"},
    "DreamContent": {"content","writer","writing","podcast","video","audio","script","blog","newsletter","editorial"},
    "DreamCrypto": {"crypto","blockchain","wallet","token","on-chain","defi","digital asset","testnet"},
    "DreamCustIntel": {"customer intelligence","customer feedback","retention","churn","journey","segmentation","customer research","voice of customer"},
    "DreamCyber": {"cyber","security","vulnerability","threat","incident","identity security","hardening","soc","secure coding"},
    "DreamData": {"data","dataset","etl","analytics","database","warehouse","pipeline","data quality","data governance","sql"},
    "DreamDecision": {"decision","scenario","tradeoff","risk comparison","decision support","uncertainty","option analysis"},
    "DreamEducation": {"education","student","teacher","tutor","course","lesson","curriculum","quiz","learning","training"},
    "DreamEmpire": {"portfolio","enterprise strategy","capital allocation","executive","governance","cross-division","empire"},
    "DreamEntFinance": {"enterprise finance","treasury","controller","budgeting","financial planning","fp&a","management reporting","cash forecast"},
    "DreamFinance": {"finance","budget","cash flow","financial","saving","wealth","expense","personal finance","investment education"},
    "DreamFlow": {"handoff","queue","dependency","process map","task flow","work graph","sla","workflow analytics"},
    "DreamFood": {"food","restaurant","menu","kitchen","recipe","inventory","allergen","catering","meal"},
    "DreamGlobal": {"global","international","country","localization","culture","market entry","sanctions","cross-border"},
    "DreamHealth": {"health","medical","patient","wellness","care","clinical","provider","symptom education","records"},
    "DreamInfluence": {"influencer","creator growth","sponsor","brand deal","audience","campaign","partnership","influence"},
    "DreamLegal": {"legal","law","contract","attorney","court","statute","compliance","case","legal research"},
    "DreamLoans": {"loan","lending","credit","financing","mortgage","apr","borrower","underwriting","repayment"},
    "DreamMaintenance": {"maintenance","repair","work order","preventive","equipment","parts","inspection","reliability"},
    "DreamMarket": {"market research","market","competitor","demand","pricing","opportunity","market sizing","trend"},
    "DreamMilitary": {"military","veteran","readiness","service member","defense logistics","base operations"},
    "DreamOps": {"operations","capacity","incident","service level","operating","process control","kpi","operations management"},
    "DreamPayments": {"payment","checkout","billing","subscription","merchant","processor","chargeback","stripe","transaction"},
    "DreamPersonalCare": {"personal care","grooming","beauty","skincare","hair","routine","self care","cosmetic"},
    "DreamPlanetary": {"climate","planet","earth","space","environment","disaster","energy","satellite","geospatial"},
    "DreamProServices": {"professional service","consultant","client intake","proposal","expert","credential","service firm","bookkeeping service"},
    "DreamProduction": {"manufacturing","production","factory","bom","quality control","assembly","oem","odm","robotics manufacturing"},
    "DreamProtection": {"protection","safety","fraud","scam","emergency","risk protection","preparedness","personal safety"},
    "DreamRealEstate": {"real estate","property","rental","landlord","tenant","homebuyer","house","listing","property management","realtor"},
    "DreamRetail": {"retail","store","inventory","product catalog","ecommerce","shop","merchandise","point of sale","sku"},
    "DreamSalesPro": {"sales","lead","prospect","outreach","crm","cold email","cold call","closer","objection","pipeline","sdr"},
    "DreamScience": {"science","research","experiment","physics","chemistry","biology","laboratory","scientific","hypothesis"},
    "DreamSocial": {"social media","social","community manager","post","instagram","tiktok","linkedin","facebook","social listening"},
    "DreamTrade": {"trade","import","export","supplier","sourcing","tariff","customs","wholesale","b2b sourcing"},
    "DreamTransport": {"transport","fleet","route","shipping","driver","vehicle","logistics","delivery","dispatch"},
    "GameTitan": {"game","gaming","npc","game engine","level","multiplayer","quest","unity","unreal","gameplay"},
}

# Keywords whose appearance should outweigh generic overlaps.
STRONG = {"mortgage","blockchain","game engine","legal research","customer intelligence","enterprise finance","personal care","social media","real estate","government contracting","multi-agent","cold email","chargeback","manufacturing"}
TOKEN_RE = re.compile(r"[a-z0-9+#.-]+")


def normalize(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.lower()))


def bot_text(bot: dict) -> str:
    values = [bot.get("slug", ""), bot.get("displayName", ""), bot.get("category", ""), bot.get("description", ""), bot.get("targetUsers", ""), bot.get("revenueModel", "")]
    values.extend(bot.get("capabilities", []) or [])
    return normalize(" ".join(str(v) for v in values))


def score(text: str, division: str) -> tuple[int, list[str]]:
    hits: list[str] = []
    points = 0
    for kw in KEYWORDS[division]:
        if kw in text:
            hits.append(kw)
            points += 4 if kw in STRONG or " " in kw else 2
    # Division-name concept hint without using the literal current file as proof.
    return points, sorted(set(hits))


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    rows: list[dict] = []
    seen_slugs: dict[str, list[str]] = defaultdict(list)
    source_counts: Counter[str] = Counter()
    missing_files: list[str] = []
    source_mismatches: list[dict] = []

    for division in DIVISIONS:
        path = APP_BOTS / f"{division}.json"
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)))
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        declared = payload.get("division")
        if declared != division:
            source_mismatches.append({"file": str(path.relative_to(ROOT)), "expected": division, "declared": declared})
        bots = payload.get("bots", [])
        source_counts[division] += len(bots)
        for bot in bots:
            slug = str(bot.get("slug", "")).strip()
            if slug:
                seen_slugs[slug].append(division)
            text = bot_text(bot)
            scored = []
            for candidate in DIVISIONS:
                pts, hits = score(text, candidate)
                scored.append((pts, candidate, hits))
            scored.sort(key=lambda item: (-item[0], item[1]))
            current_score, current_hits = next((p, h) for p, d, h in scored if d == division)
            best_score, best_division, best_hits = scored[0]
            second_score = scored[1][0] if len(scored) > 1 else 0
            margin = best_score - current_score
            if best_division == division:
                status = "well_placed"
            elif best_score >= 8 and margin >= 6:
                status = "move_candidate"
            elif best_score >= 6 and margin >= 3:
                status = "review_cross_division"
            else:
                status = "keep_low_confidence"
            collaborators = [d for p, d, _ in scored[1:4] if p >= max(4, best_score - 4) and d != division]
            rows.append({
                "slug": slug,
                "display_name": bot.get("displayName"),
                "current_division": division,
                "category": bot.get("category"),
                "status": status,
                "current_score": current_score,
                "current_hits": current_hits,
                "recommended_primary": best_division,
                "recommended_score": best_score,
                "recommended_hits": best_hits,
                "score_margin_vs_current": margin,
                "second_best_score": second_score,
                "suggested_collaborators": collaborators,
                "source": str(path.relative_to(ROOT)),
            })

    duplicate_slugs = [{"slug": slug, "divisions": ds} for slug, ds in sorted(seen_slugs.items()) if len(ds) > 1]
    status_counts = Counter(row["status"] for row in rows)
    division_summary = {}
    for division in DIVISIONS:
        division_rows = [r for r in rows if r["current_division"] == division]
        division_summary[division] = {
            "profile_count": len(division_rows),
            "well_placed": sum(r["status"] == "well_placed" for r in division_rows),
            "move_candidates": sum(r["status"] == "move_candidate" for r in division_rows),
            "review_cross_division": sum(r["status"] == "review_cross_division" for r in division_rows),
            "low_confidence": sum(r["status"] == "keep_low_confidence" for r in division_rows),
            "strengthening": config["division_plans"][division]["strengthen"],
            "collaborators": config["division_plans"][division]["collaborators"],
        }

    payload = {
        "schema": "dreamco.bot_division_placement_audit.v1",
        "source": "App_bots/*.json",
        "expected_divisions": len(DIVISIONS),
        "profiles_scanned": len(rows),
        "status_counts": dict(status_counts),
        "missing_division_files": missing_files,
        "source_division_mismatches": source_mismatches,
        "duplicate_slugs": duplicate_slugs,
        "division_summary": division_summary,
        "bots": rows,
        "truth_boundary": "Keyword scoring is a triage aid, not proof of placement. Move candidates require human/canonical-owner review and regression testing before source files change."
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md = ["# Bot Division Placement Audit", "", f"Profiles scanned: **{len(rows)}** across **{len(DIVISIONS)}** expected divisions.", "", "## Fleet placement status", ""]
    for key in ["well_placed","review_cross_division","move_candidate","keep_low_confidence"]:
        md.append(f"- `{key}`: {status_counts.get(key, 0)}")
    md += ["", "## Division strengthening and placement", "", "| Division | Profiles | Move candidates | Cross-division review | Strengthen next |", "| --- | ---: | ---: | ---: | --- |"]
    for division in DIVISIONS:
        s = division_summary[division]
        md.append(f"| {division} | {s['profile_count']} | {s['move_candidates']} | {s['review_cross_division']} | {'; '.join(s['strengthening'][:3])} |")
    candidates = [r for r in rows if r["status"] == "move_candidate"]
    md += ["", "## Move candidates", ""]
    if candidates:
        for r in candidates:
            md.append(f"- `{r['slug']}`: {r['current_division']} → **{r['recommended_primary']}** (current {r['current_score']}, recommended {r['recommended_score']}; hits: {', '.join(r['recommended_hits'])})")
    else:
        md.append("- None exceeded the automatic review threshold.")
    if duplicate_slugs:
        md += ["", "## Duplicate slugs", ""] + [f"- `{r['slug']}`: {', '.join(r['divisions'])}" for r in duplicate_slugs]
    md += ["", "## Rule", "", "This report recommends. It does not auto-move bots. Any move must update the canonical source, generated fleet artifacts, tests, benchmark ownership, business blueprint references, and cross-division collaboration metadata together.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "ok": not missing_files and not source_mismatches and not duplicate_slugs,
        "profiles_scanned": len(rows),
        "divisions": len(DIVISIONS),
        "status_counts": dict(status_counts),
        "duplicate_slugs": len(duplicate_slugs),
        "missing_division_files": len(missing_files),
        "source_division_mismatches": len(source_mismatches),
        "json": str(OUT_JSON.relative_to(ROOT)),
        "report": str(OUT_MD.relative_to(ROOT)),
    }, indent=2))
    return 0 if not missing_files and not source_mismatches and not duplicate_slugs else 1


if __name__ == "__main__":
    raise SystemExit(main())
