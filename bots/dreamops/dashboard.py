"""
DreamOps Dashboard renderer.

Provides formatted summary views for all DreamOps subsystems.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from framework import GlobalAISourcesFlow  # noqa: F401

from datetime import datetime


def render_anomaly_summary(detector) -> str:
    """Render a text summary of anomaly alerts."""
    summary = detector.summary()
    lines = ["── Anomaly Detection ──────────────────"]
    lines.append(f"  Total Alerts  : {summary['total']}")
    for severity, count in summary["by_severity"].items():
        lines.append(f"  {severity:<10}: {count}")
    return "\n".join(lines)


def render_scaling_status(engine) -> str:
    """Render scaling engine status."""
    history = engine.get_scaling_history()
    lines = ["── Auto-Scaling ────────────────────────"]
    lines.append(f"  Scaling Events : {len(history)}")
    if history:
        last = history[-1]
        lines.append(f"  Last Action    : {last['action']} on {last['task_id']}")
    else:
        lines.append("  Last Action    : none")
    return "\n".join(lines)


def render_ops_status(commander) -> str:
    """Render operations commander status."""
    report = commander.get_status_report()
    lines = ["── Ops Commander ───────────────────────"]
    lines.append(f"  Total Systems  : {report['total_systems']}")
    lines.append(f"  Healthy        : {report['healthy']}")
    lines.append(f"  Degraded       : {report['degraded']}")
    lines.append(f"  Open Incidents : {report['open_incidents']}")
    return "\n".join(lines)


def render_bottleneck_map(detector) -> str:
    """Render bottleneck summary."""
    bottlenecks = detector.get_bottlenecks()
    lines = ["── Bottleneck Detector ─────────────────"]
    lines.append(f"  Detected       : {len(bottlenecks)}")
    for b in bottlenecks[:3]:
        lines.append(f"  [{b.severity_score:.1f}] Stage {b.stage_id} in {b.workflow_id}")
    return "\n".join(lines)


def render_failover_status(failover) -> str:
    """Render failover status."""
    status = failover.get_failover_status()
    lines = ["── Auto-Failover ───────────────────────"]
    lines.append(f"  Failover Pairs : {len(status['failover_pairs'])}")
    lines.append(f"  Total Events   : {status['total_events']}")
    for pair in status["failover_pairs"][:2]:
        active = pair["currently_active"]
        lines.append(f"  {pair['primary_id']} → active: {active}")
    return "\n".join(lines)


def render_cost_summary(engine) -> str:
    """Render cost reduction summary."""
    savings = engine.estimate_savings()
    lines = ["── Cost Reduction ──────────────────────"]
    lines.append(f"  Departments    : {savings['total_departments']}")
    lines.append(f"  Monthly Savings: ${savings['total_estimated_monthly_savings_usd']:,.2f}")
    lines.append(f"  Annual Savings : ${savings['total_estimated_annual_savings_usd']:,.2f}")
    return "\n".join(lines)


def render_throughput_report(maximizer) -> str:
    """Render throughput maximizer report."""
    report = maximizer.get_optimization_report()
    lines = ["── Throughput Maximizer ────────────────"]
    lines.append(f"  Flows Analyzed : {report['total_flows']}")
    lines.append(f"  Constraints    : {report['total_constraints_identified']}")
    lines.append(f"  Optimizations  : {report['optimization_runs']}")
    return "\n".join(lines)


def render_full_dashboard(dreamops_bot) -> str:
    """Render the full DreamOps dashboard."""
    header = (
        "╔══════════════════════════════════════════╗\n"
        "║       DreamOps AI Automation Suite       ║\n"
        f"║  Tier: {dreamops_bot.tier.value.upper():<10}  "
        f"  {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC  ║\n"
        "╚══════════════════════════════════════════╝"
    )
    sections = [header]
    sections.append(render_anomaly_summary(dreamops_bot.anomaly_detector))
    sections.append(render_scaling_status(dreamops_bot.scaling_engine))
    sections.append(render_ops_status(dreamops_bot.ops_commander))
    sections.append(render_bottleneck_map(dreamops_bot.bottleneck_detector))
    sections.append(render_failover_status(dreamops_bot.auto_failover))
    sections.append(render_cost_summary(dreamops_bot.cost_engine))
    sections.append(render_throughput_report(dreamops_bot.throughput_maximizer))
    return "\n".join(sections)
