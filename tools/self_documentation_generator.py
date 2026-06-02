from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import ast

@dataclass
class DocumentationArtifact:
    markdown_path: Path
    openapi_path: Path
    undocumented_functions: List[str]


class SelfDocumentationGenerator:
    def generate(self, source_path: str, slug: str) -> DocumentationArtifact:
        source = Path(source_path)
        tree = ast.parse(source.read_text())
        methods: List[Dict[str, str]] = []
        undocumented: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node)
                if not doc:
                    undocumented.append(node.name)
                methods.append({'name': node.name, 'doc': doc or 'TODO: add docstring', 'params': ', '.join(arg.arg for arg in node.args.args)})
        docs_dir = source.parent.parent / 'docs' / 'auto'
        docs_dir.mkdir(parents=True, exist_ok=True)
        md_path = docs_dir / f'{slug}.md'
        yaml_path = docs_dir / f'{slug}.yaml'
        md_path.write_text(self._markdown(source, methods, undocumented))
        yaml_path.write_text(self._openapi(slug, methods))
        return DocumentationArtifact(markdown_path=md_path, openapi_path=yaml_path, undocumented_functions=undocumented)

    def _markdown(self, source: Path, methods: List[Dict[str, str]], undocumented: List[str]) -> str:
        lines = [f'# {source.stem}', '', '## Overview', f'Auto-generated documentation for `{source.name}`.', '', '## Methods']
        for method in methods:
            lines.extend([f"### {method['name']}", f"Parameters: {method['params']}", method['doc'], '', 'Examples: import and call the function or class method directly.', 'Pricing: internal utility, no direct charge.', ''])
        if undocumented:
            lines.extend(['## Undocumented Functions', ', '.join(undocumented), 'Add docstrings to improve generated docs quality.'])
        return '
'.join(lines)

    def _openapi(self, slug: str, methods: List[Dict[str, str]]) -> str:
        lines = ['openapi: 3.0.0', f'info:
  title: {slug}
  version: 1.0.0', 'paths:']
        for method in methods:
            lines.extend([f'  /{method["name"]}:', '    post:', f'      summary: {method["doc"][:60]}', '      responses:', "        '200':", '          description: OK'])
        return '
'.join(lines)



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}
