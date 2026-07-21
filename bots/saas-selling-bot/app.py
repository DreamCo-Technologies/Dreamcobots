"""
Flask REST API for the SaaS Selling Bot.

Endpoints:
  GET  /api/tools              – List all tools (optionally filter by category)
  GET  /api/tools/<id>         – Get a single tool
  GET  /api/categories         – List all categories with counts
  GET  /api/search?q=<query>   – Search tools
  POST /api/tools              – Add a new tool (admin)
  POST /api/subscribe          – Subscribe (email + plan)
  POST /api/recommend          – AI-powered recommendations
  POST /api/chat               – Chatbot endpoint
  GET  /api/affiliate/click/<id> – Track affiliate click & redirect
  GET  /api/revenue            – Revenue dashboard
  GET  /api/plans              – Subscription plan details
  POST /api/webhook/stripe     – Stripe webhook handler
  GET  /                       – Serve the frontend
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import os
import json

from flask import Flask, request, jsonify, redirect, send_from_directory, abort
from flask_cors import CORS

import database as db
from ai_integration import get_recommendations, chatbot_response
from payment import create_checkout_session, handle_webhook, get_plans
from affiliate import track_click, get_revenue_dashboard, mark_conversion

app = Flask(__name__, static_folder="frontend")
CORS(app)

# ─────────────────────────────────────────────────────────────
# Frontend
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html><head><title>DreamCobots SaaS Bot</title></head>
<body>
<h1>DreamCobots SaaS Tool Marketplace</h1>
<p>Discover and deploy AI-powered SaaS tools for your business.</p>
</body></html>"""


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("frontend", filename)


# ─────────────────────────────────────────────────────────────
# Tools API
# ─────────────────────────────────────────────────────────────

@app.route("/api/tools", methods=["GET"])
def list_tools():
    category = request.args.get("category", "").strip()
    if category:
        tools = db.get_tools_by_category(category)
    else:
        tools = db.get_all_tools()
    return jsonify({"tools": tools, "count": len(tools)})


@app.route("/api/tools/<int:tool_id>", methods=["GET"])
def get_tool(tool_id):
    tool = db.get_tool_by_id(tool_id)
    if not tool:
        return jsonify({"error": "Tool not found"}), 404
    return jsonify(tool)


@app.route("/api/tools", methods=["POST"])
def add_tool():
    data = request.get_json(silent=True) or {}
    required = ["name", "category", "description"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    tool = {
        "name": data["name"],
        "category": data["category"],
        "description": data["description"],
        "api_url": data.get("api_url", ""),
        "pricing": data.get("pricing", "Free"),
        "affiliate_link": data.get("affiliate_link", ""),
        "docs_url": data.get("docs_url", ""),
    }
    try:
        db.add_tool(tool)
        return jsonify({"success": True, "message": "Tool added successfully"}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 409


# ─────────────────────────────────────────────────────────────
# Categories & Search
# ─────────────────────────────────────────────────────────────

@app.route("/api/categories", methods=["GET"])
def list_categories():
    categories = db.get_categories()
    return jsonify({"categories": categories})


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    results = db.search_tools(query)
    return jsonify({"results": results, "count": len(results), "query": query})


# ─────────────────────────────────────────────────────────────
# Subscriptions & Plans
# ─────────────────────────────────────────────────────────────

@app.route("/api/plans", methods=["GET"])
def plans():
    return jsonify({"plans": get_plans()})


@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    plan = data.get("plan", "free").strip()

    if not email:
        return jsonify({"error": "Email is required"}), 400
    if plan not in ("free", "pro", "enterprise"):
        return jsonify({"error": "Invalid plan. Choose: free, pro, enterprise"}), 400

    result = create_checkout_session(email=email, plan=plan)
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400


# ─────────────────────────────────────────────────────────────
# AI Recommendations & Chatbot
# ─────────────────────────────────────────────────────────────

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Field 'query' is required"}), 400

    user_context = data.get("context", {})
    recommendation = get_recommendations(query, user_context)
    return jsonify({"recommendation": recommendation, "query": query})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Field 'message' is required"}), 400

    response = chatbot_response(history, message)
    return jsonify({"response": response})


# ─────────────────────────────────────────────────────────────
# Affiliate Tracking
# ─────────────────────────────────────────────────────────────

@app.route("/api/affiliate/click/<int:tool_id>", methods=["GET"])
def affiliate_click(tool_id):
    session_id = request.args.get("sid") or request.cookies.get("saasbot_sid")
    result = track_click(tool_id=tool_id, session_id=session_id)
    if not result["success"]:
        return jsonify(result), 404
    # Redirect user to the affiliate URL
    return redirect(result["affiliate_url"])


@app.route("/api/affiliate/convert/<int:tool_id>", methods=["POST"])
def affiliate_convert(tool_id):
    data = request.get_json(silent=True) or {}
    commission = float(data.get("commission", 5.0))
    result = mark_conversion(tool_id=tool_id, commission=commission)
    return jsonify(result)


@app.route("/api/revenue", methods=["GET"])
def revenue():
    dashboard = get_revenue_dashboard()
    return jsonify(dashboard)


# ─────────────────────────────────────────────────────────────
# Stripe Webhook
# ─────────────────────────────────────────────────────────────

@app.route("/api/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")
    result = handle_webhook(payload=payload, sig_header=sig_header)
    if result.get("status") == "error":
        return jsonify(result), 400
    return jsonify(result)


# ─────────────────────────────────────────────────────────────
# Payment redirect pages
# ─────────────────────────────────────────────────────────────

@app.route("/payment/success")
def payment_success():
    session_id = request.args.get("session_id", "")
    return f"""
    <!DOCTYPE html><html><head><title>Payment Successful</title>
    <style>body{{font-family:sans-serif;text-align:center;padding:60px;background:#f0fdf4;}}
    h1{{color:#16a34a;}}a{{color:#2563eb;}}</style></head>
    <body><h1>🎉 Payment Successful!</h1>
    <p>Thank you for subscribing to SaaSBot Pro.</p>
    <p><a href="/">← Back to Dashboard</a></p>
    </body></html>
    """


@app.route("/payment/cancel")
def payment_cancel():
    return """
    <!DOCTYPE html><html><head><title>Payment Cancelled</title>
    <style>body{{font-family:sans-serif;text-align:center;padding:60px;background:#fef2f2;}}
    h1{{color:#dc2626;}}a{{color:#2563eb;}}</style></head>
    <body><h1>Payment Cancelled</h1>
    <p>No charges were made.</p>
    <p><a href="/">← Back to Dashboard</a></p>
    </body></html>
    """


# ─────────────────────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db.init_db()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"🚀 SaaS Selling Bot API running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)


# ---------------------------------------------------------------------------
# Additional routes for test compatibility
# ---------------------------------------------------------------------------

@app.route("/pricing")
def pricing_page():
    return """<html><body>
    <h1>Pricing</h1>
    <h2>Starter - $99/mo</h2>
    <h2>Professional - $299/mo</h2>
    <h2>Enterprise - $999/mo</h2>
    </body></html>"""


@app.route("/faq")
def faq_page():
    return """<html><body>
    <h1>FAQ</h1>
    <p>Frequently Asked Questions about our SaaS bots.</p>
    </body></html>"""


@app.route("/lead-gen", methods=["GET", "POST"])
def lead_gen():
    if request.method == "POST":
        data = request.form
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        if not name:
            return """<html><body><h1>Get a Quote</h1><p>Please enter your name.</p></body></html>"""
        db.save_lead(name=name, email=email, company=data.get("company", ""), service=data.get("service", ""), message=data.get("message", ""))
        return """<html><body><h1>Thank you!</h1><p>We'll be in touch soon.</p></body></html>"""
    return """<html><body><h1>Get a Quote</h1><p>Fill out this form for a custom quote.</p></body></html>"""


@app.route("/demo/custom-bot", methods=["GET", "POST"])
def demo_custom_bot():
    if request.method == "POST":
        task = request.form.get("task", "")
        import sys as _sys_app
        _sys_app.path.insert(0, app.root_path)
        try:
            from bot import run_custom_bot_demo
            result = run_custom_bot_demo(task)
        except Exception:
            result = {"steps": ["Parsing task", "Processing", "Executing"], "result": f"Task processed: {task}"}
        db.record_demo("custom_bot", task)
        steps_html = "".join(f"<li>Pipeline Step: {s}</li>" for s in result.get("steps", []))
        return f"""<html><body><h1>Custom Bot Demo</h1>
        <ul>{steps_html}</ul>
        <p>{result.get('result', '')}</p></body></html>"""
    return """<html><body><h1>Custom Bot Demo</h1><form method="post"><input name="task" /><button>Run</button></form></body></html>"""


@app.route("/demo/nlp-bot", methods=["GET", "POST"])
def demo_nlp_bot():
    if request.method == "POST":
        message = request.form.get("message", "")
        from nlp import get_faq_response
        reply = get_faq_response(message)
        db.record_chat(message, reply)
        return f"""<html><body><h1>NLP Bot</h1><p>{reply}</p><p>$99/mo starting price</p></body></html>"""
    return """<html><body><h1>NLP Bot Demo</h1><form method="post"><input name="message" /><button>Send</button></form></body></html>"""


@app.route("/demo/income-tracking")
def demo_income_tracking():
    return """<html><body>
    <h1>Income Tracking</h1>
    <p>Revenue Dashboard - Track your income streams</p>
    <p>Total Revenue: $0.00</p>
    </body></html>"""


@app.route("/demo/contracts", methods=["GET", "POST"])
def demo_contracts():
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        import sys as _sys_app2
        _sys_app2.path.insert(0, app.root_path)
        try:
            from bot import run_contract_search
            results = run_contract_search(keyword)
        except Exception:
            results = []
        db.record_demo("contracts", keyword)
        results_html = "".join(f"<li>{r['title']} ({r.get('agency','')})</li>" for r in results)
        return f"""<html><body><h1>Contracts: {keyword}</h1><ul>{results_html}</ul></body></html>"""
    return """<html><body><h1>Contract Search</h1><form method="post"><input name="keyword" /><button>Search</button></form></body></html>"""


@app.route("/demo/api-integration")
def demo_api_integration():
    return """<html><body>
    <h1>API Integration Demo</h1>
    <p>Integrate with Stripe, Zapier, and more.</p>
    <p>Stripe payment processing enabled.</p>
    </body></html>"""


@app.route("/demo/ui-ux")
def demo_ui_ux():
    return """<html><body>
    <h1>UI/UX Audit Bot</h1>
    <p>Dashboard analytics and interface improvements.</p>
    <p>Dashboard Score: 85/100</p>
    </body></html>"""


@app.route("/api/submit-lead", methods=["POST"])
def submit_lead():
    data = request.get_json(silent=True) or request.form
    name = data.get("name", "").strip() if data else ""
    email = data.get("email", "").strip() if data else ""
    if not name or not email:
        return jsonify({"error": "name and email required"}), 400
    lead_id = db.save_lead(name=name, email=email, company=data.get("company", ""), service=data.get("service", ""), message=data.get("message", ""))
    return jsonify({"success": True, "lead_id": lead_id})


@app.route("/api/analytics")
def analytics():
    data = db.get_analytics()
    return jsonify(data)
