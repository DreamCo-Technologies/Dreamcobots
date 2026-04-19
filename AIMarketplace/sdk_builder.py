# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
SDK Builder — AI Marketplace

Generates Python and Node.js SDK stubs for marketplace products.

Usage
-----
    from AIMarketplace.sdk_builder import SDKBuilder

    builder = SDKBuilder()
    py_stub = builder.generate_python("abc123", "dreammimic_voice")
    js_stub = builder.generate_nodejs("abc123", "dreammimic-voice")
    print(py_stub)
    print(js_stub)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Dict


@dataclass
class SDKStub:
    sdk_id: str
    product_id: str
    language: str
    package_name: str
    entry_point: str
    readme_snippet: str

    def to_dict(self) -> dict:
        return {
            "sdk_id": self.sdk_id,
            "product_id": self.product_id,
            "language": self.language,
            "package_name": self.package_name,
            "entry_point": self.entry_point,
            "readme_snippet": self.readme_snippet,
        }


class SDKBuilder:
    """Generates lightweight SDK stubs for Python and Node.js."""

    def __init__(self) -> None:
        self._stubs: Dict[str, SDKStub] = {}

    def generate_python(self, product_id: str, package_name: str) -> dict:
        """
        Generate a Python SDK stub for a marketplace product.

        Returns a serialised :class:`SDKStub`.
        """
        class_name = "".join(p.capitalize() for p in package_name.replace("-", "_").split("_"))
        entry = f"from {package_name} import {class_name}"
        readme = (
            f"# {package_name} — Python SDK\n\n"
            f"```bash\npip install {package_name}\n```\n\n"
            f"```python\n{entry}\n"
            f"bot = {class_name}()\nresult = bot.run({{}})\nprint(result)\n```"
        )
        stub = SDKStub(
            sdk_id=str(uuid.uuid4())[:8],
            product_id=product_id,
            language="python",
            package_name=package_name,
            entry_point=entry,
            readme_snippet=readme,
        )
        self._stubs[stub.sdk_id] = stub
        return stub.to_dict()

    def generate_nodejs(self, product_id: str, package_name: str) -> dict:
        """
        Generate a Node.js SDK stub for a marketplace product.

        Returns a serialised :class:`SDKStub`.
        """
        class_name = "".join(p.capitalize() for p in package_name.replace("-", "_").split("_"))
        entry = f"const {{ {class_name} }} = require('{package_name}');"
        readme = (
            f"# {package_name} — Node.js SDK\n\n"
            f"```bash\nnpm install {package_name}\n```\n\n"
            f"```js\n{entry}\n"
            f"const bot = new {class_name}();\nconst result = await bot.run({{}});\nconsole.log(result);\n```"
        )
        stub = SDKStub(
            sdk_id=str(uuid.uuid4())[:8],
            product_id=product_id,
            language="nodejs",
            package_name=package_name,
            entry_point=entry,
            readme_snippet=readme,
        )
        self._stubs[stub.sdk_id] = stub
        return stub.to_dict()

    def list_stubs(self) -> list:
        """Return all generated SDK stubs."""
        return [s.to_dict() for s in self._stubs.values()]
