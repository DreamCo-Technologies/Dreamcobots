import ast
from pathlib import Path


def test_intake_parser_entrypoint_compiles():
    source = Path("stages/02_intake_parser/__main__.py").read_text(encoding="utf-8")
    compile(source, "stages/02_intake_parser/__main__.py", "exec")
    ast.parse(source)
