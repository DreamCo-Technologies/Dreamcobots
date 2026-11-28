"""Permit shared Actions caches only for signed, publicly redistributable training inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from .guardrails import verify_signed_manifest


def public_cache_allowed(manifest: dict) -> bool:
    datasets = manifest.get("datasets", [])
    models = manifest.get("models", [])
    resources = list(datasets) + list(models)
    return bool(datasets) and all(
        item.get("cache_visibility") == "public"
        and item.get("redistribution_allowed") is True
        for item in resources
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = verify_signed_manifest(args.manifest, args.signature, args.public_key)
    allowed = public_cache_allowed(manifest)
    digest = hashlib.sha256()
    source_paths = [
        args.manifest,
        args.recipe,
        Path("stages/05_model_foundry/train_tokenizer.py"),
        Path("stages/05_model_foundry/pack_tokens.py"),
        Path("stages/05_model_foundry/cache_policy.py"),
    ]
    for path in source_paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\\0")
        digest.update(path.read_bytes())
        digest.update(b"\\0")
    key = digest.hexdigest()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"cache_allowed": allowed, "cache_key": key}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"cache_allowed={'true' if allowed else 'false'}\n")
            stream.write(f"cache_key={key}\n")
    print(json.dumps({"cache_allowed": allowed, "cache_key": key}, sort_keys=True))


if __name__ == "__main__":
    main()
