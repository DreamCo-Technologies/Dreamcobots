"""Shared gate + config logic. Plan-only until every gate is green."""
import argparse, json, os, sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]


def load_yaml(p):
    import yaml  # lazy
    return yaml.safe_load(Path(p).read_text())


def gates_green():
    g = json.loads((PACK / "gates.json").read_text())["gates"]
    bad = [x["id"] for x in g if x["status"] != "green" or not x.get("evidence")]
    return not bad, bad


def parse(method):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(PACK / "recipes" / f"{method}.yaml"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cfg = load_yaml(a.config)
    assert cfg["method"] == method, "config/method mismatch"
    for k in ("base_model", "dataset", "lora", "trainer_args"):
        assert k in cfg, f"missing {k}"
    print(f"[plan] {cfg['pack_id']} base={cfg['base_model']} data={cfg['dataset']['id']}")
    print(f"[plan] trainer_args={json.dumps(cfg['trainer_args'])}")
    if a.dry_run:
        print("[dry-run] config valid; no training performed")
        sys.exit(0)
    ok, bad = gates_green()
    if os.environ.get("APPROVED_RUN") != "1" or not ok:
        print(f"[refused] APPROVED_RUN={os.environ.get('APPROVED_RUN')} pending_gates={bad}")
        sys.exit(2)
    return cfg


def lora(cfg):
    from peft import LoraConfig
    return LoraConfig(**cfg["lora"])


def dataset(cfg):
    from datasets import load_dataset
    return load_dataset(cfg["dataset"]["id"], split=cfg["dataset"]["split"])
