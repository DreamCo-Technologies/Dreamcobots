"""Original study-guide contract validation and conservative similarity gate."""
from __future__ import annotations
import re
from collections import Counter
from typing import Any

REQUIRED = ("guide_id", "title", "learning_objectives", "lesson", "practice_lab", "assessment", "safety_notes")
def validate_guide(guide: dict[str, Any]) -> list[str]:
    errors=[]
    for key in REQUIRED:
        if key not in guide: errors.append(f"missing:{key}")
    for key in ("learning_objectives","safety_notes"):
        if key in guide and (not isinstance(guide[key],list) or not guide[key]): errors.append(f"invalid:{key}")
    for key in ("guide_id","title","lesson","practice_lab","assessment"):
        if key in guide and (not isinstance(guide[key],str) or not guide[key].strip()): errors.append(f"invalid:{key}")
    if "provenance" in guide: errors.append("provenance_must_be_stored_outside_learner_guide")
    return errors

def _ngrams(text: str, n: int=5) -> set[tuple[str,...]]:
    tokens=re.findall(r"[a-z0-9_]+",text.lower())
    if not tokens: return set()
    return {tuple(tokens[i:i+n]) for i in range(max(1,len(tokens)-n+1))}

def similarity_ratio(candidate: str, reference: str) -> float:
    """Jaccard overlap of token n-grams; a heuristic, not a legal determination."""
    a,b=_ngrams(candidate),_ngrams(reference)
    if not a or not b: return 0.0
    return len(a&b)/len(a|b)

def clean_room_gate(guide: dict[str,Any], references: list[str], threshold: float=0.18) -> dict[str,Any]:
    errors=validate_guide(guide)
    scores=[similarity_ratio(" ".join(str(v) for v in guide.values() if isinstance(v,(str,list))),ref) for ref in references]
    maximum=max(scores,default=0.0)
    return {"accepted":not errors and maximum < threshold,"validation_errors":errors,
            "max_ngram_jaccard":round(maximum,6),"threshold":threshold,
            "similarity_method":"token_5gram_jaccard_heuristic",
            "requires_human_rights_review":True,
            "warning":"Similarity screening is not proof of originality, non-infringement, or rights clearance."}
