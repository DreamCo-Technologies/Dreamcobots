from __future__ import annotations

import ast
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import List


@dataclass
class DiscoveredCapability:
    name: str
    signature: str
    summary: str
    keywords: List[str]


class CapabilityDiscovery:
    def scan(self, bot_path: str) -> List[DiscoveredCapability]:
        root = Path(bot_path)
        capabilities: list[DiscoveredCapability] = []
        for file in root.rglob('*.py'):
            tree = ast.parse(file.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    doc = ast.get_docstring(node) or ''
                    summary = doc.splitlines()[0] if doc else f'Public function {node.name}'
                    signature = f"{node.name}({', '.join(arg.arg for arg in node.args.args)})"
                    capabilities.append(
                        DiscoveredCapability(
                            name=node.name,
                            signature=signature,
                            summary=summary,
                            keywords=self._extract_keywords(doc or node.name),
                        )
                    )
        self._update_profile(root, capabilities)
        return capabilities

    def _extract_keywords(self, text: str) -> List[str]:
        tokens = [token.lower() for token in re.findall(r'[A-Za-z]{4,}', text)]
        seen = []
        for token in tokens:
            if token not in seen:
                seen.append(token)
        return seen[:8]

    def _update_profile(self, root: Path, capabilities: List[DiscoveredCapability]) -> None:
        profile_path = root / 'bot_profile.json'
        profile = {}
        if profile_path.exists():
            profile = json.loads(profile_path.read_text(encoding='utf-8'))
        profile['capabilities'] = [cap.name for cap in capabilities]
        profile['capability_details'] = [cap.__dict__ for cap in capabilities]
        profile_path.write_text(json.dumps(profile, indent=2), encoding='utf-8')

def capability_matrix(self, capabilities: List[DiscoveredCapability]) -> dict:
    return {
        capability.name: {
            'signature': capability.signature,
            'keywords': capability.keywords,
            'summary': capability.summary,
        }
        for capability in capabilities
    }


def describe_capabilities(self, capabilities: List[DiscoveredCapability]) -> str:
    parts = []
    for capability in capabilities:
        parts.append(f"{capability.name}: {capability.summary}")
    return "\n".join(parts)


CapabilityDiscovery.capability_matrix = capability_matrix
CapabilityDiscovery.describe_capabilities = describe_capabilities
