"""
Run All Bots — Orchestrates the full DreamCo revenue pipeline.

Pipeline:
  1. Lead generation (lead_bot)
  2. Email outreach (outreach_bot)
  3. Real estate deal discovery (real_estate_bot)
  4. Sales conversion (sales_bot)
"""

from __future__ import annotations

import importlib.util
import os
import sys


def _load_bot(filename: str, module_name: str):
    """Load a standalone bot module by file path, bypassing package conflicts."""
    path = os.path.join(os.path.dirname(__file__), "bots", filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Import standalone pipeline bots directly from their source files to avoid
# shadowing by identically-named subpackages (e.g. bots/sales_bot/).
_lead_bot = _load_bot("lead_bot.py", "_pipeline_lead_bot")
_outreach_bot = _load_bot("outreach_bot.py", "_pipeline_outreach_bot")
_sales_bot = _load_bot("sales_bot.py", "_pipeline_sales_bot")
_real_estate_bot = _load_bot("real_estate_bot.py", "_pipeline_real_estate_bot")

run_leads = _lead_bot.run_leads
send_message = _outreach_bot.send_message
close_sales = _sales_bot.close_sales
find_deals = _real_estate_bot.find_deals


def main() -> None:
    """Execute the full revenue pipeline."""
    leads = run_leads()

    for lead in leads:
        send_message(lead)

    deals = find_deals(leads)
    revenue = close_sales(leads)

    print(f"Deals Found: {len(deals)}")
    print(f"Revenue: ${revenue:.2f}")


if __name__ == "__main__":
    main()
