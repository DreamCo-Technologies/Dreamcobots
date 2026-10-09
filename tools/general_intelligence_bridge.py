"""Review routes for the existing loopback Buddy bridge, not a second server."""
from __future__ import annotations

import secrets
import json
from http import HTTPStatus


def private_snapshot(store):
    actions, audit = store.queue(), store.audit()
    with store.connect() as db:
        has_horizons = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='horizons'").fetchone()
        horizons = [json.loads(r[0]) for r in db.execute("SELECT body FROM horizons")] if has_horizons else []
    completed = [a for a in actions if a["status"] in {"verified", "failed"}]
    promotions = [a for a in actions if a["action"]["action_class"] in {"model_promotion", "rollback"}]
    evidence_reviews = [{"parameters": a["action"]["parameters"], "status": a["status"], "action_hash": a["hash"]}
                        for a in actions if a["action"]["action_class"] == "evidence_review" and a["reviewer"]]
    return {"actions": actions, "audit": audit, "horizons": horizons, "promotions": promotions,
            "evidence_reviews": evidence_reviews, "interventions": {
                "scope": "local completed actions, not model benchmark accuracy", "count": len(completed),
                "rate": sum(bool(a["reviewer"]) for a in completed) / len(completed) if completed else None}}


def handle_review(handler, method, path):
    if not path.startswith("/api/local/evaluation/"):
        return False
    state = handler.state
    store = getattr(state, "review_store", None)
    if store is None:
        handler._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Start Buddy with --review-console; public Pages cannot authorize actions."})
        return True
    host = handler.headers.get("Host", "")
    port = handler.server.server_address[1]
    if host not in {f"127.0.0.1:{port}", f"localhost:{port}"}:
        handler._json(HTTPStatus.FORBIDDEN, {"error": "Loopback host required"})
        return True
    origin = handler.headers.get("Origin")
    if origin and origin != f"http://{host}":
        handler._json(HTTPStatus.FORBIDDEN, {"error": "Same-origin review required"})
        return True
    proposal = method == "POST" and path == "/api/local/evaluation/propose"
    expected_token = state.token if proposal else getattr(state, "review_token", "")
    if not expected_token or not secrets.compare_digest(handler.headers.get("Authorization", ""), f"Bearer {expected_token}"):
        handler._json(HTTPStatus.UNAUTHORIZED, {"error": "Separate human reviewer session required" if not proposal else "Agent session required"})
        return True
    try:
        if method == "GET" and path == "/api/local/evaluation/queue":
            handler._json(HTTPStatus.OK, {**private_snapshot(store), "reviewer": state.reviewer_id})
        elif method == "POST":
            if state.paused:
                handler._json(HTTPStatus.LOCKED, {"error": "Buddy is paused"})
                return True
            payload = handler._payload()
            if proposal:
                action_id = store.propose(payload["action"], payload.get("autonomy", "Guided"))
                handler._json(HTTPStatus.CREATED, {"id": action_id, "status": "queued_for_review"})
            elif path == "/api/local/evaluation/decide":
                row = store.decide(payload["id"], payload["revision"], payload["decision"], state.reviewer_id,
                                   edited=payload.get("edited"), note=payload.get("note", ""))
                handler._json(HTTPStatus.OK, {"action": row})
            else:
                handler._json(HTTPStatus.NOT_FOUND, {"error": "Unknown review operation"})
        else:
            handler._json(HTTPStatus.NOT_FOUND, {"error": "Unknown review operation"})
    except (ValueError, KeyError, TypeError) as error:
        handler._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
    except Exception:
        handler._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Review storage failed; action remains blocked"})
    return True
