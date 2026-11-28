import ast
from pathlib import Path


def test_sandbox_verifier_entrypoint_compiles():
    source = Path("stages/05_sandbox_verifier/__main__.py").read_text(encoding="utf-8")
    compile(source, "stages/05_sandbox_verifier/__main__.py", "exec")
    ast.parse(source)
