#!/usr/bin/env python3
"""Download the current public O*NET task-statements export and build curricula.

The official database files are public downloads. No O*NET API key is needed.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from build_onet_task_curricula import build, read_rows

SOURCE_PAGE = "https://www.onetcenter.org/database.html"
USER_AGENT = "DreamCo-Buddy-Bootcamp/1.0 (O*NET attribution preserved)"


class DownloadLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.page_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_data(self, data: str) -> None:
        self.page_text.append(data)


def discover_json_links(parser: DownloadLinkParser) -> dict[str, str]:
    """Return exact JSON download links from the official O*NET database page."""
    discovered: dict[str, str] = {}
    for href in parser.links:
        path = href.split("?", 1)[0]
        if "/dl_files/database/" not in path:
            continue
        filename = path.rsplit("/", 1)[-1]
        if not filename.lower().endswith(".json"):
            continue
        key = filename[:-5]
        if key:
            discovered[key] = href
    return discovered


def fetch_current_export() -> tuple[bytes, str, str]:
    request = urllib.request.Request(SOURCE_PAGE, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = DownloadLinkParser()
    parser.feed(html)
    discovered = discover_json_links(parser)
    href = discovered.get("task_statements")
    if not href:
        raise RuntimeError("Could not locate the official current O*NET task_statements.json link; refusing to use a stale guessed URL.")
    if href.startswith("/"):
        url = "https://www.onetcenter.org" + href
    elif href.startswith("http"):
        url = href
    else:
        url = "https://www.onetcenter.org/" + href.lstrip("./")
    text = " ".join(parser.page_text)
    match = re.search(r"O\*NET\s*(?:®|&reg;)?\s*([0-9]+\.[0-9]+)\s*Database", text, re.I)
    version = match.group(1) if match else "current-release-version-unparsed"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read()
    return payload, version, url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--minimum-task-count", type=int, default=10000)
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload, version, source_url = fetch_current_export()
    raw_path = out / "onet-task-statements.json"
    raw_path.write_bytes(payload)
    rows = read_rows(raw_path)
    result = build(rows, version)
    result["source"]["official_download_url"] = source_url
    result["source"]["release_page"] = SOURCE_PAGE
    result["source"]["license"] = "Creative Commons Attribution 4.0 International; verify current O*NET license terms and preserve attribution."
    result["inventory"]["download_bytes"] = len(payload)
    result["inventory"]["coverage_check"] = {
        "minimum_task_count": args.minimum_task_count,
        "passed": result["inventory"]["task_statements"] >= args.minimum_task_count,
    }
    if result["inventory"]["task_statements"] < args.minimum_task_count:
        raise SystemExit(
            f"Incomplete O*NET task export: {result['inventory']['task_statements']} "
            f"tasks; expected at least {args.minimum_task_count}."
        )
    (out / "onet-task-curricula.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# O*NET occupation and task curricula", "",
        f"- O*NET release: {version}",
        f"- Occupations: {result['inventory']['occupations']}",
        f"- Task statements: {result['inventory']['task_statements']}",
        f"- Official export: {source_url}",
        "- Rights: O*NET database attribution and license terms must be preserved.",
        "- Each task is assigned a Buddy study/practice and supervised business/community pathway brief.",
        "- These are learning plans, not professional credentials or authorization to perform regulated work.",
    ]
    (out / "onet-task-curricula.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps(result["inventory"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
