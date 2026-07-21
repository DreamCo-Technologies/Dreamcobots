"""
Affiliate link tracking and revenue recording for the SaaS Selling Bot.
Tracks clicks on affiliate links, records conversions, and provides
revenue analytics.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import uuid
from database import (
    record_affiliate_click,
    record_conversion,
    get_revenue_summary,
    get_tool_by_id,
    get_connection,
)


def generate_session_id() -> str:
    """Generate a unique session identifier for tracking."""
    return str(uuid.uuid4())


def track_click(tool_id: int, session_id: str = None) -> dict:
    """
    Record an affiliate link click.
    Returns the tool's affiliate URL to redirect the user.
    """
    tool = get_tool_by_id(tool_id)
    if not tool:
        return {"success": False, "error": "Tool not found"}

    sid = session_id or generate_session_id()
    record_affiliate_click(tool_id=tool_id, session_id=sid)

    return {
        "success": True,
        "session_id": sid,
        "affiliate_url": tool["affiliate_link"],
        "tool_name": tool["name"],
    }


def mark_conversion(tool_id: int, commission: float = 5.0) -> dict:
    """
    Mark an affiliate click as converted and record the commission.
    commission: amount in USD earned from the conversion.
    """
    tool = get_tool_by_id(tool_id)
    if not tool:
        return {"success": False, "error": "Tool not found"}

    record_conversion(tool_id=tool_id, commission=commission)
    return {
        "success": True,
        "tool_name": tool["name"],
        "commission_recorded": commission,
    }


def get_top_tools(limit: int = 10) -> list:
    """Return the top tools ranked by affiliate click count."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.id, t.name, t.category, t.affiliate_link,
                  COUNT(ac.id) AS click_count,
                  SUM(COALESCE(ac.commission, 0)) AS total_commission
           FROM tools t
           LEFT JOIN affiliate_clicks ac ON t.id = ac.tool_id
           GROUP BY t.id
           ORDER BY click_count DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_revenue_dashboard() -> dict:
    """Return a full revenue and affiliate dashboard summary."""
    summary = get_revenue_summary()
    top = get_top_tools(5)
    conn = get_connection()
    daily_revenue = conn.execute(
        """SELECT DATE(recorded_at) as day, SUM(amount) as amount
           FROM revenue
           GROUP BY day
           ORDER BY day DESC
           LIMIT 30"""
    ).fetchall()
    conn.close()
    return {
        "summary": summary,
        "top_tools": top,
        "daily_revenue": [dict(r) for r in daily_revenue],
    }


if __name__ == "__main__":
    dashboard = get_revenue_dashboard()
    print("Revenue Dashboard:")
    print(f"  Total Revenue : ${dashboard['summary']['total_revenue']:.2f}")
    print(f"  Total Clicks  : {dashboard['summary']['total_clicks']}")
    print(f"  Conversions   : {dashboard['summary']['conversions']}")
    print("\nTop Tools by Clicks:")
    for t in dashboard["top_tools"]:
        print(f"  {t['name']} ({t['category']}) – {t['click_count']} clicks")
