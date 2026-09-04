#!/usr/bin/env python3
"""Safe local file conversion engine for Buddy.

Supports deterministic text/data conversions in the standard library and
optionally delegates office/document/media formats to installed, pinned tools.
No shell interpolation is used. Inputs are size-limited and outputs are written
only beneath an explicit output directory.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 100 * 1024 * 1024
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".html", ".htm", ".xml", ".yaml", ".yml"}
SUPPORTED = {"txt", "md", "html", "csv", "json", "xml", "yaml", "yml", "pdf", "docx", "xlsx", "pptx", "odt", "ods", "odp"}


def _safe_name(name: str) -> str:
    return Path(name).stem.replace("/", "_").replace("\\", "_")[:120] or "converted"


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _load_structured(path: Path) -> Any:
    suffix = path.suffix.lower()
    text = _load_text(path)
    if suffix == ".json":
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("YAML conversion requires PyYAML") from exc
        return yaml.safe_load(text)
    if suffix == ".csv":
        rows = list(csv.DictReader(text.splitlines()))
        return rows
    return text


def _to_text(data: Any) -> str:
    if isinstance(data, str):
        return data
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _standard_convert(src: Path, dst: Path, target: str) -> bool:
    source_ext = src.suffix.lower()
    if source_ext not in TEXT_EXTENSIONS:
        return False
    data = _load_structured(src)
    target = target.lower().lstrip(".")
    if target == "json":
        payload = data if not isinstance(data, str) else {"text": data}
        dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        return True
    if target == "csv":
        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise ValueError("CSV output requires a list of object records")
        keys = sorted({k for row in data for k in row})
        with dst.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader(); writer.writerows(data)
        return True
    text = _to_text(data)
    if target == "html":
        dst.write_text("<!doctype html><meta charset=\"utf-8\"><pre>" + html.escape(text) + "</pre>\n", encoding="utf-8")
    else:
        dst.write_text(text, encoding="utf-8")
    return True


def _libreoffice_convert(src: Path, output_dir: Path, target: str) -> Path | None:
    binary = shutil.which("libreoffice") or shutil.which("soffice")
    if not binary:
        return None
    target = target.lower().lstrip(".")
    with tempfile.TemporaryDirectory(prefix="dreamco-convert-") as profile:
        cmd = [binary, "--headless", "--nologo", "--nodefault", "--nofirststartwizard", f"-env:UserInstallation=file://{profile}", "--convert-to", target, "--outdir", str(output_dir), str(src)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "LibreOffice conversion failed")[-4000:])
    expected = output_dir / f"{src.stem}.{target}"
    return expected if expected.exists() else None


def _pandoc_convert(src: Path, output: Path, target: str) -> bool:
    binary = shutil.which("pandoc")
    if not binary:
        return False
    result = subprocess.run([binary, str(src), "-o", str(output)], capture_output=True, text=True, timeout=120, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "Pandoc conversion failed")[-4000:])
    return output.exists()


def convert(src: str, target: str, output_dir: str) -> Path:
    source = Path(src).expanduser().resolve()
    out = Path(output_dir).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} byte limit")
    target = target.lower().lstrip(".")
    if target not in SUPPORTED:
        raise ValueError(f"unsupported target format: {target}")
    out.mkdir(parents=True, exist_ok=True)
    destination = out / f"{_safe_name(source.name)}.{target}"
    if destination.resolve().parent != out:
        raise ValueError("invalid output path")
    if _standard_convert(source, destination, target):
        return destination
    if target in {"md", "html", "txt", "pdf", "docx", "odt", "epub"} and _pandoc_convert(source, destination, target):
        return destination
    converted = _libreoffice_convert(source, out, target)
    if converted:
        return converted
    raise RuntimeError(f"no installed converter supports {source.suffix} -> {target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("--output-dir", default="./converted")
    args = parser.parse_args()
    result = convert(args.source, args.target, args.output_dir)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
