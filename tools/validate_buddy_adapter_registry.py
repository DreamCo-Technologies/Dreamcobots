"""Validate the Buddy student adapter registry.

Rule: trained_weights_exist may be true only when every listed artifact exists
on disk with a matching sha256 and byte size, plus a model card and eval scorecard.
"""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "config" / "buddy-student-adapter-registry.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
TRAINED_STATES = {"trained", "evaluated", "released"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(reg: dict, root: Path = ROOT) -> list:
    errs = []
    if reg.get("schema") != "dreamco.buddy_student_adapter_registry.v1":
        errs.append("bad schema id")
    if not SEMVER.match(str(reg.get("registry_version", ""))):
        errs.append("registry_version must be semver")
    truth = reg.get("truth", {})
    if truth.get("frontier_parity_proven") is not False:
        errs.append("frontier_parity_proven must stay false in this registry")
    seen, any_real = set(), False
    for a in reg.get("adapters", []):
        key = (a.get("id"), a.get("version"))
        if key in seen:
            errs.append(f"duplicate {key}")
        seen.add(key)
        if not SEMVER.match(str(a.get("version", ""))):
            errs.append(f"{a.get('id')}: version must be semver")
        claims = a.get("trained_weights_exist") is True
        arts = a.get("artifacts") or []
        if claims:
            if not arts:
                errs.append(f"{a['id']}: trained_weights_exist true with no artifacts")
            for art in arts:
                p = root / art["path"]
                if not p.is_file():
                    errs.append(f"{a['id']}: missing artifact {art['path']}")
                    continue
                if p.stat().st_size != art["bytes"]:
                    errs.append(f"{a['id']}: size mismatch {art['path']}")
                if sha256(p) != art["sha256"]:
                    errs.append(f"{a['id']}: sha256 mismatch {art['path']}")
            if not a.get("model_card"):
                errs.append(f"{a['id']}: trained_weights_exist true without model_card")
            if not (a.get("evidence") or {}).get("eval_scorecard"):
                errs.append(f"{a['id']}: trained_weights_exist true without eval_scorecard")
            any_real = any_real or not errs
        elif a.get("status") in TRAINED_STATES:
            errs.append(f"{a['id']}: status {a['status']} requires trained_weights_exist true")
    if truth.get("trained_weights_exist") and not any_real:
        errs.append("top-level trained_weights_exist true but no adapter proves it")
    return errs


def main() -> int:
    errs = validate(json.loads(REG.read_text(encoding="utf-8")))
    for e in errs:
        print("ERROR:", e)
    print("OK" if not errs else f"{len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
