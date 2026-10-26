"""Static, read-only repository-wide source discovery; no code imports or execution."""
import ast
import hashlib
import json
import re
from pathlib import Path

IGNORE = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".next", "coverage", "vendor"}
MAX_BYTES = 1024 * 1024
EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".cs", ".rb", ".php", ".sh"}
def discover(root):
    root = Path(root).resolve()
    results, skipped = [], 0
    for p in sorted(root.rglob("*")):
        if not p.is_file() or any(part in IGNORE for part in p.relative_to(root).parts):
            continue
        rel = p.relative_to(root).as_posix()
        if p.stat().st_size > MAX_BYTES:
            skipped += 1
            continue
        if p.suffix not in EXTS and not (rel.startswith(".github/workflows/") and p.suffix in (".yml", ".yaml")) and p.name not in ("package.json", "requirements.txt", "pyproject.toml"):
            continue
        try:
            raw = p.read_bytes()
            source = raw.decode("utf-8")
        except (UnicodeError, OSError):
            skipped += 1
            continue
        digest = hashlib.sha256(raw).hexdigest()
        def add(kind, name, line):
            results.append({"id": f"{rel}:{line}:{name}", "kind": kind, "source": rel,
                            "line": line, "name": name, "source_sha256": digest,
                            "status": "discovered_not_tested"})
        if rel.startswith(".github/workflows/") and p.suffix in (".yml", ".yaml"):
            add("workflow", p.stem, 1)
        elif p.suffix == ".py":
            try:
                tree = ast.parse(source, filename=rel)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        add("function", node.name, node.lineno)
                    elif isinstance(node, ast.ClassDef):
                        add("capability", node.name, node.lineno)
            except SyntaxError:
                skipped += 1
        elif p.name in ("package.json", "requirements.txt", "pyproject.toml"):
            add("library", p.name, 1)
        else:
            for m in re.finditer(r"(?m)^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)", source):
                add("function", m.group(1), source.count("\n", 0, m.start()) + 1)
        if "generat" in p.stem.lower() or p.stem.startswith("build_"):
            add("generator", p.stem, 1)
        if p.name.startswith("tool_") or "/tools/" in "/" + rel:
            add("tool", p.stem, 1)
    return {"schema": "dreamco.repository_discovery.v1", "scope": "static source inventory",
            "counts": {"symbols": len(results), "skipped_files": skipped},
            "items": results, "warning": "Source presence is not capability, functionality or mastery."}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="website/data/buddy-repository-discovery.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    dest = (root / args.output).resolve()
    if not dest.is_relative_to(root / "website" / "data"):
        parser.error("output must be under website/data")
    report = discover(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"]))

if __name__ == "__main__":
    main()
