"""Unified DreamCo Empire OS CLI powered by Click and Rich."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[1]
console = Console()


def _run(command: list[str], dry_run: bool) -> int:
    console.print(f"[cyan]$ {' '.join(command)}[/cyan]")
    if dry_run:
        return 0
    return subprocess.run(command, cwd=ROOT, check=False).returncode


@click.group()
def cli() -> None:
    """DreamCo Empire OS unified command line entrypoint."""


@cli.group()
def bot() -> None:
    """Bot lifecycle commands."""


@bot.command("run")
@click.argument("slug")
@click.option("--dry-run", is_flag=True)
def bot_run(slug: str, dry_run: bool) -> None:
    _run(["python", f"bots/{slug}/main.py"], dry_run)


@bot.command("benchmark")
@click.option("--dry-run", is_flag=True)
def bot_benchmark(dry_run: bool) -> None:
    _run(["python", "tools/bot_benchmark_runner.py"], dry_run)


@bot.command("deploy")
@click.argument("slug")
@click.option("--dry-run", is_flag=True)
def bot_deploy(slug: str, dry_run: bool) -> None:
    _run(["python", "-c", f"print('deploy {slug}')"], dry_run)


@cli.command("registry-validate")
@click.option("--dry-run", is_flag=True)
def registry_validate(dry_run: bool) -> None:
    _run(["python", "tools/extended_compliance_checker.py"], dry_run)


@cli.command("registry-drift")
@click.option("--dry-run", is_flag=True)
def registry_drift(dry_run: bool) -> None:
    _run(["python", "tools/registry_drift_detector.py"], dry_run)


@cli.command("report-investor")
@click.option("--dry-run", is_flag=True)
def report_investor(dry_run: bool) -> None:
    _run(["python", "tools/investor_report_generator.py"], dry_run)


@cli.command("sandbox-start")
@click.argument("slug")
@click.option("--dry-run", is_flag=True)
def sandbox_start(slug: str, dry_run: bool) -> None:
    _run(["python", "-c", f"print('sandbox start {slug}')"], dry_run)


@cli.command("sandbox-stop")
@click.argument("slug")
@click.option("--dry-run", is_flag=True)
def sandbox_stop(slug: str, dry_run: bool) -> None:
    _run(["python", "-c", f"print('sandbox stop {slug}')"], dry_run)


if __name__ == "__main__":
    cli()
