"""Real deterministic stateful tool-execution sandbox with bounded actions."""
import hashlib
import json

ALLOWED = {"read_inventory", "read_reserved", "calculate_available", "publish"}
def execute(steps, *, inventory=8, reserved=3):
    if len(steps) > 12:
        raise ValueError("too many tool actions")
    state = {"inventory": inventory, "reserved": reserved, "available": None, "published": False}
    receipts = []
    for action in steps:
        if action not in ALLOWED:
            raise ValueError("unapproved tool action")
        if action == "read_inventory":
            output = state["inventory"]
        elif action == "read_reserved":
            output = state["reserved"]
        elif action == "calculate_available":
            state["available"] = state["inventory"] - state["reserved"]
            output = state["available"]
        else:
            if state["available"] is None or state["available"] < 0:
                receipts.append({"action": action, "status": "blocked", "reason": "invalid prerequisite"})
                break
            state["published"] = True
            output = True
        receipts.append({"action": action, "status": "success", "output": output})
    digest = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    return {"schema": "dreamco.tool_execution_receipt.v1", "state": state,
            "receipts": receipts, "state_sha256": digest,
            "real_external_actions": False, "sandbox_executed": True}
