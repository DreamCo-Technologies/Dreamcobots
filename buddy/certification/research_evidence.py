"""Offline research evidence verifier: authored source passages, IDs and answer entailment.

No web retrieval. A passing result means support in a provided source fixture,
NOT that a source is authentic or independently audited.
"""
import hashlib
import re

def verify_research_answer(answer, task):
    sources=task.get("sources",[])
    if not isinstance(sources,list) or not sources:
        return {"passed":False,"reason":"no_source_evidence","source_verified":False}
    if not all(isinstance(s,dict) and isinstance(s.get("id"),str)
               and isinstance(s.get("text"),str) and s["text"] for s in sources):
        return {"passed":False,"reason":"invalid_source_fixture","source_verified":False}
    if len({s["id"] for s in sources})!=len(sources):
        return {"passed":False,"reason":"duplicate_source_ids","source_verified":False}
    # Require a JSON response with an answer and source IDs, avoiding uncheckable citations.
    import json
    try:
        response=json.loads(answer)
        value=response["answer"]
        cited=response["source_ids"]
        if not isinstance(value,str) or not isinstance(cited,list) or not cited:
            raise ValueError()
        if not all(isinstance(x,str) for x in cited):
            raise ValueError()
    except (ValueError,TypeError,KeyError):
        return {"passed":False,"reason":"invalid_cited_answer","source_verified":False}
    ids={s["id"] for s in sources}
    if not set(cited).issubset(ids):
        return {"passed":False,"reason":"unknown_source","source_verified":False}
    expected=task.get("expected")
    if not isinstance(expected,str) or value.strip().casefold()!=expected.strip().casefold():
        return {"passed":False,"reason":"incorrect_answer","source_verified":False}
    # Explicit source evidence must support the canonical answer; this is not
    # semantic entailment or proof of external provenance.
    support=[s for s in sources if s["id"] in cited and
             re.search(r"(?<!\\w)"+re.escape(expected.strip())+r"(?!\\w)",
                       s["text"],flags=re.IGNORECASE)]
    if not support:
        return {"passed":False,"reason":"cited_passage_does_not_contain_answer","source_verified":False}
    return {"passed":True,"reason":"fixture_source_support",
            "source_verified":False,"fixture_supported":True,
            "source_receipts":[{"id":s["id"],"sha256":hashlib.sha256(s["text"].encode()).hexdigest()}
                               for s in support]}
