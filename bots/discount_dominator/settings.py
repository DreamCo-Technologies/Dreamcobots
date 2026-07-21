"""
Discount Dominator Settings (401–600).

This module defines the numbered settings that power the Discount Dominator
system across all Dreamcobots bots.  Settings are organised into five
functional groups:

  401–450  Advanced Analytics
  451–500  In-Store Tactical Controls
  501–550  Online Platform Optimization
  551–580  Enterprise-Grade Features
  581–600  Behavioral Settings

Each setting is stored as a typed entry in ``DISCOUNT_DOMINATOR_SETTINGS``.
Use :func:`get_setting` and :func:`apply_settings` to read and apply them.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Setting:
    """A single Discount Dominator configuration entry.

    Attributes
    ----------
    id : int
        Unique setting number (401–600).
    name : str
        Human-readable identifier (``snake_case``).
    group : str
        Functional group this setting belongs to.
    description : str
        Plain-English explanation of what the setting controls.
    default : Any
        Default value used when not explicitly overridden.
    value : Any
        Current runtime value (defaults to ``default``).
    """

    id: int
    name: str
    group: str
    description: str
    default: Any
    value: Any = field(default=None)

    def __post_init__(self) -> None:
        if self.value is None:
            self.value = self.default

    def reset(self) -> None:
        """Restore this setting to its default value."""
        self.value = self.default


# ---------------------------------------------------------------------------
# Group labels
# ---------------------------------------------------------------------------

GROUP_ANALYTICS = "advanced_analytics"
GROUP_INSTORE = "in_store_tactical_controls"
GROUP_ONLINE = "online_platform_optimization"
GROUP_ENTERPRISE = "enterprise_grade_features"
GROUP_BEHAVIORAL = "behavioral_settings"

# ---------------------------------------------------------------------------
# Settings 401–450: Advanced Analytics
# ---------------------------------------------------------------------------

_ANALYTICS: list[Setting] = [
    Setting(401, "realtime_analytics_enabled", GROUP_ANALYTICS,
            "Enable streaming real-time analytics pipeline.", True),
    Setting(402, "analytics_retention_days", GROUP_ANALYTICS,
            "Number of days to retain raw analytics data.", 90),
    Setting(403, "custom_metric_tracking", GROUP_ANALYTICS,
            "Allow user-defined custom KPI metrics.", True),
    Setting(404, "competitor_price_monitoring", GROUP_ANALYTICS,
            "Continuously monitor and log competitor pricing signals.", True),
    Setting(405, "market_trend_analysis", GROUP_ANALYTICS,
            "Run automated market-trend analysis on ingested data.", True),
    Setting(406, "demand_forecasting_enabled", GROUP_ANALYTICS,
            "Use ML models to forecast future demand per SKU.", True),
    Setting(407, "cohort_analysis_enabled", GROUP_ANALYTICS,
            "Segment users into cohorts for longitudinal analysis.", True),
    Setting(408, "funnel_analysis_enabled", GROUP_ANALYTICS,
            "Visualise conversion funnels across channels.", True),
    Setting(409, "revenue_attribution_model", GROUP_ANALYTICS,
            "Attribution model: first_touch|last_touch|linear|data_driven.",
            "data_driven"),
    Setting(410, "real_estate_price_index", GROUP_ANALYTICS,
            "Track real estate pricing indices to support RES optimisation.",
            True),
    Setting(411, "auto_parts_market_feed", GROUP_ANALYTICS,
            "Integrate auto-parts market data feed for car-flipping bot.",
            True),
    Setting(412, "retail_basket_analysis", GROUP_ANALYTICS,
            "Run market-basket analysis on retail transaction streams.", True),
    Setting(413, "cross_channel_attribution", GROUP_ANALYTICS,
            "Attribute conversions across in-store and online channels.", True),
    Setting(414, "anomaly_detection_enabled", GROUP_ANALYTICS,
            "Flag statistical anomalies in sales and traffic data.", True),
    Setting(415, "inventory_turnover_tracking", GROUP_ANALYTICS,
            "Track and report inventory-turnover ratios per category.", True),
    Setting(416, "return_rate_analysis", GROUP_ANALYTICS,
            "Analyse product return rates and root-cause drivers.", True),
    Setting(417, "customer_lifetime_value_model", GROUP_ANALYTICS,
            "Predict CLV using RFM and ML regression models.", "rfm_ml"),
    Setting(418, "price_elasticity_modelling", GROUP_ANALYTICS,
            "Model demand sensitivity to price changes per SKU.", True),
    Setting(419, "geo_heatmap_analytics", GROUP_ANALYTICS,
            "Render geographic heat maps of sales density.", True),
    Setting(420, "session_replay_analytics", GROUP_ANALYTICS,
            "Enable session-replay data collection for UX analytics.", False),
    Setting(421, "ab_test_framework", GROUP_ANALYTICS,
            "Built-in A/B and multivariate testing framework.", True),
    Setting(422, "predictive_restocking", GROUP_ANALYTICS,
            "Trigger restocking orders based on predictive stock-out models.",
            True),
    Setting(423, "margin_analytics_enabled", GROUP_ANALYTICS,
            "Calculate and surface gross/net margin per product line.", True),
    Setting(424, "supplier_performance_index", GROUP_ANALYTICS,
            "Score supplier delivery, quality, and cost performance.", True),
    Setting(425, "social_sentiment_feed", GROUP_ANALYTICS,
            "Ingest social-media sentiment as an analytics signal.", True),
    Setting(426, "search_trend_integration", GROUP_ANALYTICS,
            "Pull search-volume trends from integrated search platforms.",
            True),
    Setting(427, "cross_bot_data_sharing", GROUP_ANALYTICS,
            "Share anonymised analytics across registered Dreamcobots bots.",
            True),
    Setting(428, "analytics_export_format", GROUP_ANALYTICS,
            "Default export format for analytics reports: csv|json|parquet.",
            "json"),
    Setting(429, "analytics_alert_threshold_pct", GROUP_ANALYTICS,
            "Percentage deviation that triggers an analytics alert.", 10),
    Setting(430, "analytics_dashboard_refresh_sec", GROUP_ANALYTICS,
            "Dashboard auto-refresh interval in seconds.", 60),
    Setting(431, "multi_currency_analytics", GROUP_ANALYTICS,
            "Normalise revenue figures to a base currency for analytics.",
            True),
    Setting(432, "base_currency", GROUP_ANALYTICS,
            "ISO 4217 base currency for normalised reporting.", "USD"),
    Setting(433, "tax_inclusive_reporting", GROUP_ANALYTICS,
            "Report revenue figures inclusive of taxes.", False),
    Setting(434, "channel_mix_report", GROUP_ANALYTICS,
            "Generate weekly channel-mix performance report.", True),
    Setting(435, "nlp_review_summarisation", GROUP_ANALYTICS,
            "Auto-summarise customer reviews using NLP.", True),
    Setting(436, "voice_of_customer_index", GROUP_ANALYTICS,
            "Compute a Voice-of-Customer score from review sentiment.", True),
    Setting(437, "store_traffic_analytics", GROUP_ANALYTICS,
            "Ingest and analyse in-store foot-traffic data.", True),
    Setting(438, "online_traffic_analytics", GROUP_ANALYTICS,
            "Track and analyse e-commerce site traffic.", True),
    Setting(439, "cart_abandonment_rate_tracking", GROUP_ANALYTICS,
            "Monitor cart-abandonment rates per channel.", True),
    Setting(440, "loyalty_redemption_analytics", GROUP_ANALYTICS,
            "Analyse loyalty-point redemption patterns.", True),
    Setting(441, "partner_sales_analytics", GROUP_ANALYTICS,
            "Track sales through partner and affiliate channels.", True),
    Setting(442, "workforce_productivity_index", GROUP_ANALYTICS,
            "Measure store-staff productivity via task-completion metrics.",
            True),
    Setting(443, "shrinkage_loss_tracking", GROUP_ANALYTICS,
            "Track inventory shrinkage and loss events.", True),
    Setting(444, "promotion_roi_analysis", GROUP_ANALYTICS,
            "Calculate ROI for each promotional campaign.", True),
    Setting(445, "dynamic_report_scheduling", GROUP_ANALYTICS,
            "Schedule automated report delivery to stakeholders.", True),
    Setting(446, "data_lineage_tracking", GROUP_ANALYTICS,
            "Maintain full data-lineage records for compliance.", True),
    Setting(447, "real_time_kpi_alerts", GROUP_ANALYTICS,
            "Push real-time KPI breach alerts to configured channels.", True),
    Setting(448, "external_data_connectors", GROUP_ANALYTICS,
            "Enable connectors to external data sources (ERP, CRM, etc.).",
            True),
    Setting(449, "analytics_api_enabled", GROUP_ANALYTICS,
            "Expose analytics results via REST API.", True),
    Setting(450, "analytics_audit_log", GROUP_ANALYTICS,
            "Maintain a tamper-evident audit log of analytics queries.", True),
]

# ---------------------------------------------------------------------------
# Settings 451–500: In-Store Tactical Controls
# ---------------------------------------------------------------------------

_INSTORE: list[Setting] = [
    Setting(451, "instore_display_optimisation", GROUP_INSTORE,
            "Algorithmically optimise in-store product display placement.",
            True),
    Setting(452, "shelf_placement_strategy", GROUP_INSTORE,
            "Shelf-placement algorithm: eye_level|category_cluster|impulse.",
            "eye_level"),
    Setting(453, "bundle_discount_rules_enabled", GROUP_INSTORE,
            "Enable rule engine for bundle-discount configurations.", True),
    Setting(454, "flash_sale_automation", GROUP_INSTORE,
            "Auto-trigger flash sales based on inventory thresholds.", True),
    Setting(455, "loss_leader_strategy", GROUP_INSTORE,
            "Automatically designate loss-leader SKUs to drive footfall.",
            True),
    Setting(456, "endcap_rotation_schedule", GROUP_INSTORE,
            "Days between automated endcap product rotations.", 14),
    Setting(457, "price_tag_sync_enabled", GROUP_INSTORE,
            "Sync digital shelf-edge labels with live pricing data.", True),
    Setting(458, "planogram_compliance_check", GROUP_INSTORE,
            "Alert staff when planogram compliance falls below threshold.",
            True),
    Setting(459, "store_zone_optimisation", GROUP_INSTORE,
            "Optimise zone layouts based on customer flow analytics.", True),
    Setting(460, "cross_sell_signage_automation", GROUP_INSTORE,
            "Automatically update cross-sell signage near related products.",
            True),
    Setting(461, "markdown_cadence_days", GROUP_INSTORE,
            "Days between automated markdown review cycles.", 7),
    Setting(462, "seasonal_reset_automation", GROUP_INSTORE,
            "Auto-schedule seasonal section resets and restock plans.", True),
    Setting(463, "clearance_threshold_pct", GROUP_INSTORE,
            "Inventory level (%) below which clearance pricing activates.", 20),
    Setting(464, "staff_task_dispatch", GROUP_INSTORE,
            "Dispatch restock and tidy-up tasks to staff via mobile app.",
            True),
    Setting(465, "receipt_upsell_engine", GROUP_INSTORE,
            "Print targeted upsell offers on POS receipts.", True),
    Setting(466, "instore_coupon_generation", GROUP_INSTORE,
            "Generate personalised in-store coupons at checkout.", True),
    Setting(467, "pos_integration_enabled", GROUP_INSTORE,
            "Integrate with Point-of-Sale systems for live transaction data.",
            True),
    Setting(468, "self_checkout_optimisation", GROUP_INSTORE,
            "Apply intelligent queue-management at self-checkout lanes.", True),
    Setting(469, "fitting_room_tracking", GROUP_INSTORE,
            "Track fitting-room usage to surface conversion insights.", False),
    Setting(470, "instore_wifi_analytics", GROUP_INSTORE,
            "Leverage Wi-Fi probe data for dwell-time analytics.", True),
    Setting(471, "digital_signage_content_sync", GROUP_INSTORE,
            "Push promotion content to in-store digital signage.", True),
    Setting(472, "real_time_stock_visibility", GROUP_INSTORE,
            "Show real-time stock levels on customer-facing displays.", True),
    Setting(473, "instore_event_automation", GROUP_INSTORE,
            "Automate scheduling and promotion of in-store events.", True),
    Setting(474, "shrinkage_alert_zones", GROUP_INSTORE,
            "Define high-risk zones and trigger shrinkage alerts.", True),
    Setting(475, "weight_based_pricing", GROUP_INSTORE,
            "Enable weight-based pricing for bulk product sections.", False),
    Setting(476, "instore_loyalty_kiosk", GROUP_INSTORE,
            "Enable self-service loyalty check-in kiosks in-store.", True),
    Setting(477, "smart_cart_integration", GROUP_INSTORE,
            "Integrate with smart cart platforms for scan-and-go.", False),
    Setting(478, "vendor_managed_inventory", GROUP_INSTORE,
            "Allow vendors to manage their own shelf replenishment.", True),
    Setting(479, "mystery_shopper_module", GROUP_INSTORE,
            "Schedule and score automated mystery-shopper audits.", True),
    Setting(480, "instore_ar_enabled", GROUP_INSTORE,
            "Enable AR wayfinding and product discovery overlays.", False),
    Setting(481, "theft_deterrent_alerts", GROUP_INSTORE,
            "Integrate with security systems for theft-deterrent alerts.",
            True),
    Setting(482, "perishable_markdown_automation", GROUP_INSTORE,
            "Auto-mark down perishables approaching expiry dates.", True),
    Setting(483, "cold_chain_monitoring", GROUP_INSTORE,
            "Monitor cold-chain compliance for temperature-sensitive SKUs.",
            True),
    Setting(484, "backroom_inventory_control", GROUP_INSTORE,
            "Automate backroom stock counts and replenishment triggers.", True),
    Setting(485, "instore_promotion_effectiveness", GROUP_INSTORE,
            "Measure lift from in-store promotions vs. baseline.", True),
    Setting(486, "aisle_traffic_analysis", GROUP_INSTORE,
            "Analyse customer traffic patterns at aisle level.", True),
    Setting(487, "loyalty_points_at_pos", GROUP_INSTORE,
            "Automatically accrue and redeem loyalty points at POS.", True),
    Setting(488, "gift_card_management", GROUP_INSTORE,
            "Issue and manage gift cards through the bot ecosystem.", True),
    Setting(489, "instore_survey_kiosk", GROUP_INSTORE,
            "Deploy satisfaction-survey kiosks at exit points.", True),
    Setting(490, "associate_coaching_module", GROUP_INSTORE,
            "Surface coaching insights for floor associates via dashboard.",
            True),
    Setting(491, "instore_locator_map", GROUP_INSTORE,
            "Provide a digital aisle-map for customer product lookup.", True),
    Setting(492, "buy_online_pickup_instore", GROUP_INSTORE,
            "Enable BOPIS (Buy Online, Pick Up In-Store) workflow.", True),
    Setting(493, "instore_returns_optimisation", GROUP_INSTORE,
            "Streamline returns processing to minimise queue times.", True),
    Setting(494, "price_match_automation", GROUP_INSTORE,
            "Automate in-store price-match verification and adjustment.",
            True),
    Setting(495, "instore_digital_receipts", GROUP_INSTORE,
            "Offer digital receipts via email/SMS at POS.", True),
    Setting(496, "promotional_calendar_sync", GROUP_INSTORE,
            "Sync in-store promotions with the central promotional calendar.",
            True),
    Setting(497, "instore_mobile_payments", GROUP_INSTORE,
            "Accept mobile wallet payments at all POS terminals.", True),
    Setting(498, "instore_kpi_dashboard", GROUP_INSTORE,
            "Surface real-time KPIs on store-manager dashboard.", True),
    Setting(499, "task_completion_tracking", GROUP_INSTORE,
            "Track staff task completion rates and escalate overdue tasks.",
            True),
    Setting(500, "instore_audit_log", GROUP_INSTORE,
            "Maintain tamper-evident audit log of all in-store control events.",
            True),
]

# ---------------------------------------------------------------------------
# Settings 501–550: Online Platform Optimization
# ---------------------------------------------------------------------------

_ONLINE: list[Setting] = [
    Setting(501, "seo_optimisation_level", GROUP_ONLINE,
            "SEO aggressiveness level: basic|standard|aggressive.", "standard"),
    Setting(502, "product_listing_enhancement", GROUP_ONLINE,
            "Auto-enhance product titles, bullets, and descriptions.", True),
    Setting(503, "dynamic_pricing_rules_enabled", GROUP_ONLINE,
            "Enable dynamic pricing rule engine for online channels.", True),
    Setting(504, "cross_platform_syndication", GROUP_ONLINE,
            "Syndicate product listings across multiple marketplaces.", True),
    Setting(505, "review_management_enabled", GROUP_ONLINE,
            "Auto-request, monitor, and respond to customer reviews.", True),
    Setting(506, "sponsored_ad_automation", GROUP_ONLINE,
            "Automate sponsored-ad bidding and budget management.", True),
    Setting(507, "cart_recovery_emails", GROUP_ONLINE,
            "Send automated cart-recovery email sequences.", True),
    Setting(508, "personalised_homepage", GROUP_ONLINE,
            "Personalise online storefront based on visitor history.", True),
    Setting(509, "product_recommendation_engine", GROUP_ONLINE,
            "Show AI-powered product recommendations on listing pages.", True),
    Setting(510, "image_optimisation_enabled", GROUP_ONLINE,
            "Auto-compress and format product images for fast page loads.",
            True),
    Setting(511, "mobile_ux_optimisation", GROUP_ONLINE,
            "Apply mobile-first UX optimisations to the online storefront.",
            True),
    Setting(512, "structured_data_markup", GROUP_ONLINE,
            "Inject schema.org structured data for enhanced SERP display.",
            True),
    Setting(513, "site_speed_target_ms", GROUP_ONLINE,
            "Target page-load time in milliseconds for online platforms.", 2000),
    Setting(514, "cdn_integration_enabled", GROUP_ONLINE,
            "Route static assets through a CDN for global performance.", True),
    Setting(515, "social_commerce_enabled", GROUP_ONLINE,
            "Enable shoppable posts and social-commerce integrations.", True),
    Setting(516, "live_chat_widget", GROUP_ONLINE,
            "Embed AI-powered live-chat widget on online storefronts.", True),
    Setting(517, "onsite_search_optimisation", GROUP_ONLINE,
            "Optimise onsite search ranking and autocomplete.", True),
    Setting(518, "retargeting_pixel_enabled", GROUP_ONLINE,
            "Deploy retargeting pixels for ad re-engagement campaigns.", True),
    Setting(519, "email_newsletter_automation", GROUP_ONLINE,
            "Automate segmented newsletter send schedules.", True),
    Setting(520, "push_notification_enabled", GROUP_ONLINE,
            "Enable browser and app push notifications for promotions.", True),
    Setting(521, "sms_marketing_enabled", GROUP_ONLINE,
            "Enable opt-in SMS marketing campaign automation.", True),
    Setting(522, "affiliate_programme_enabled", GROUP_ONLINE,
            "Manage affiliate partnerships and commission tracking.", True),
    Setting(523, "influencer_campaign_tracking", GROUP_ONLINE,
            "Track influencer campaign performance and attributable revenue.",
            True),
    Setting(524, "subscription_box_module", GROUP_ONLINE,
            "Enable subscription and auto-replenishment box programme.", False),
    Setting(525, "marketplace_fee_optimiser", GROUP_ONLINE,
            "Minimise marketplace listing fees through category selection.",
            True),
    Setting(526, "buy_box_strategy", GROUP_ONLINE,
            "Strategy to win the marketplace buy box: price|fulfillment|mixed.",
            "mixed"),
    Setting(527, "flash_deal_scheduler", GROUP_ONLINE,
            "Schedule and publish online flash-deal campaigns.", True),
    Setting(528, "virtual_try_on_enabled", GROUP_ONLINE,
            "Enable AR virtual try-on for applicable product categories.",
            False),
    Setting(529, "wishlists_enabled", GROUP_ONLINE,
            "Enable customer wish-list functionality on storefront.", True),
    Setting(530, "gift_registry_enabled", GROUP_ONLINE,
            "Enable gift registry features for gifting occasions.", True),
    Setting(531, "product_comparison_tool", GROUP_ONLINE,
            "Allow customers to compare up to N products side-by-side.", True),
    Setting(532, "user_generated_content_enabled", GROUP_ONLINE,
            "Curate and display user-generated content (photos, videos).",
            True),
    Setting(533, "live_stream_commerce", GROUP_ONLINE,
            "Enable live-stream shopping events with in-stream checkout.",
            False),
    Setting(534, "b2b_portal_enabled", GROUP_ONLINE,
            "Activate a dedicated B2B portal with tiered pricing.", False),
    Setting(535, "online_returns_portal", GROUP_ONLINE,
            "Self-service online returns portal with pre-paid labels.", True),
    Setting(536, "delivery_promise_engine", GROUP_ONLINE,
            "Surface accurate delivery estimates on product pages.", True),
    Setting(537, "international_shipping_enabled", GROUP_ONLINE,
            "Enable cross-border shipping with automatic duty calculation.",
            False),
    Setting(538, "currency_auto_detect", GROUP_ONLINE,
            "Auto-detect visitor locale and display local currency prices.",
            True),
    Setting(539, "gdpr_consent_management", GROUP_ONLINE,
            "Deploy GDPR-compliant consent banner and preference centre.",
            True),
    Setting(540, "accessibility_compliance_level", GROUP_ONLINE,
            "WCAG accessibility target: A|AA|AAA.", "AA"),
    Setting(541, "checkout_optimisation_enabled", GROUP_ONLINE,
            "Apply one-page checkout and saved-payment optimisations.", True),
    Setting(542, "fraud_scoring_at_checkout", GROUP_ONLINE,
            "Score orders for fraud risk at checkout and flag high-risk.",
            True),
    Setting(543, "multi_payment_gateway", GROUP_ONLINE,
            "Support multiple payment gateways for redundancy.", True),
    Setting(544, "buy_now_pay_later_enabled", GROUP_ONLINE,
            "Integrate BNPL providers (Klarna, Afterpay, etc.).", True),
    Setting(545, "waitlist_management", GROUP_ONLINE,
            "Manage waitlists for out-of-stock items and notify customers.",
            True),
    Setting(546, "pre_order_module", GROUP_ONLINE,
            "Enable pre-order functionality for upcoming product launches.",
            True),
    Setting(547, "upsell_at_checkout", GROUP_ONLINE,
            "Display relevant upsell and cross-sell offers at checkout.",
            True),
    Setting(548, "post_purchase_survey", GROUP_ONLINE,
            "Trigger post-purchase satisfaction survey via email.", True),
    Setting(549, "dynamic_coupon_generation", GROUP_ONLINE,
            "Auto-generate personalised discount coupons for segments.", True),
    Setting(550, "online_platform_audit_log", GROUP_ONLINE,
            "Maintain tamper-evident audit log of platform optimisation events.",
            True),
]

# ---------------------------------------------------------------------------
# Settings 551–580: Enterprise-Grade Features
# ---------------------------------------------------------------------------

_ENTERPRISE: list[Setting] = [
    Setting(551, "multi_location_support", GROUP_ENTERPRISE,
            "Manage and sync configurations across multiple store locations.",
            True),
    Setting(552, "api_rate_limit_per_min", GROUP_ENTERPRISE,
            "Maximum API calls per minute per tenant.", 600),
    Setting(553, "custom_integration_hooks", GROUP_ENTERPRISE,
            "Allow custom webhook integrations for enterprise systems.", True),
    Setting(554, "compliance_monitoring_enabled", GROUP_ENTERPRISE,
            "Monitor regulatory compliance (PCI-DSS, GDPR, SOC 2).", True),
    Setting(555, "data_encryption_level", GROUP_ENTERPRISE,
            "Encryption standard: AES128|AES256.", "AES256"),
    Setting(556, "sso_enabled", GROUP_ENTERPRISE,
            "Enable Single Sign-On (SAML 2.0 / OIDC) for staff portals.",
            True),
    Setting(557, "rbac_enabled", GROUP_ENTERPRISE,
            "Enforce Role-Based Access Control across all bot modules.", True),
    Setting(558, "tenant_data_isolation", GROUP_ENTERPRISE,
            "Ensure strict data isolation between multi-tenant deployments.",
            True),
    Setting(559, "dedicated_infra_option", GROUP_ENTERPRISE,
            "Allow deployment on dedicated (non-shared) infrastructure.",
            True),
    Setting(560, "sla_uptime_target_pct", GROUP_ENTERPRISE,
            "Contractual uptime SLA target as a percentage.", 99.9),
    Setting(561, "disaster_recovery_rpo_hours", GROUP_ENTERPRISE,
            "Recovery Point Objective in hours for DR scenarios.", 4),
    Setting(562, "disaster_recovery_rto_hours", GROUP_ENTERPRISE,
            "Recovery Time Objective in hours for DR scenarios.", 2),
    Setting(563, "auto_scaling_enabled", GROUP_ENTERPRISE,
            "Automatically scale compute resources with demand.", True),
    Setting(564, "global_cdn_enabled", GROUP_ENTERPRISE,
            "Deploy assets via a global CDN for enterprise accounts.", True),
    Setting(565, "enterprise_support_channel", GROUP_ENTERPRISE,
            "Dedicated support channel: email|phone|slack|dedicated_csm.",
            "dedicated_csm"),
    Setting(566, "audit_trail_retention_years", GROUP_ENTERPRISE,
            "Years to retain full audit trail for compliance.", 7),
    Setting(567, "data_residency_region", GROUP_ENTERPRISE,
            "Enforce data residency to a specific cloud region.", "us-east-1"),
    Setting(568, "custom_branding_enabled", GROUP_ENTERPRISE,
            "Allow white-label custom branding across all bot UIs.", True),
    Setting(569, "bi_tool_integration", GROUP_ENTERPRISE,
            "Push analytics data to enterprise BI tools (Tableau, PowerBI).",
            True),
    Setting(570, "erp_integration_enabled", GROUP_ENTERPRISE,
            "Bi-directional ERP integration (SAP, Oracle, NetSuite).", True),
    Setting(571, "crm_integration_enabled", GROUP_ENTERPRISE,
            "Deep CRM integration for customer 360-degree view.", True),
    Setting(572, "wms_integration_enabled", GROUP_ENTERPRISE,
            "Warehouse Management System integration for fulfilment.", True),
    Setting(573, "oms_integration_enabled", GROUP_ENTERPRISE,
            "Order Management System integration for omnichannel orders.",
            True),
    Setting(574, "advanced_fraud_detection", GROUP_ENTERPRISE,
            "ML-powered fraud detection with configurable risk thresholds.",
            True),
    Setting(575, "ip_allowlist_enabled", GROUP_ENTERPRISE,
            "Restrict API access to a configured IP allowlist.", False),
    Setting(576, "penetration_test_schedule", GROUP_ENTERPRISE,
            "Frequency of automated pen-test runs: monthly|quarterly.",
            "quarterly"),
    Setting(577, "custom_reporting_builder", GROUP_ENTERPRISE,
            "Drag-and-drop custom report builder for enterprise users.", True),
    Setting(578, "enterprise_onboarding_support", GROUP_ENTERPRISE,
            "Dedicated onboarding support for enterprise deployments.", True),
    Setting(579, "multi_region_failover", GROUP_ENTERPRISE,
            "Automatic failover to secondary region on primary failure.", True),
    Setting(580, "enterprise_audit_log", GROUP_ENTERPRISE,
            "Centralised, tamper-evident audit log for all enterprise events.",
            True),
]

# ---------------------------------------------------------------------------
# Settings 581–600: Behavioral Settings
# ---------------------------------------------------------------------------

_BEHAVIORAL: list[Setting] = [
    Setting(581, "customer_segmentation_model", GROUP_BEHAVIORAL,
            "Segmentation model: rfm|kmeans|deep_learning.", "rfm"),
    Setting(582, "purchase_behaviour_tracking", GROUP_BEHAVIORAL,
            "Track granular purchase-behaviour signals per customer.", True),
    Setting(583, "recommendation_engine_enabled", GROUP_BEHAVIORAL,
            "Enable personalised product recommendation engine.", True),
    Setting(584, "abandoned_cart_recovery", GROUP_BEHAVIORAL,
            "Trigger automated recovery sequences for abandoned carts.", True),
    Setting(585, "loyalty_programme_integration", GROUP_BEHAVIORAL,
            "Integrate with loyalty programme for points and rewards.", True),
    Setting(586, "win_back_campaign_automation", GROUP_BEHAVIORAL,
            "Auto-trigger win-back campaigns for churned customers.", True),
    Setting(587, "churn_prediction_model", GROUP_BEHAVIORAL,
            "ML model to predict customer churn probability.", True),
    Setting(588, "next_best_action_engine", GROUP_BEHAVIORAL,
            "Determine and surface the next-best action for each customer.",
            True),
    Setting(589, "sentiment_triggered_responses", GROUP_BEHAVIORAL,
            "Trigger personalised responses based on detected sentiment.",
            True),
    Setting(590, "behavioural_email_triggers", GROUP_BEHAVIORAL,
            "Send emails triggered by specific behavioural events.", True),
    Setting(591, "browse_abandonment_recovery", GROUP_BEHAVIORAL,
            "Retarget customers who browsed but did not add to cart.", True),
    Setting(592, "real_estate_buyer_scoring", GROUP_BEHAVIORAL,
            "Score potential property buyers based on browsing behaviour.",
            True),
    Setting(593, "car_buyer_intent_model", GROUP_BEHAVIORAL,
            "Predict vehicle purchase intent for car-flipping bot targeting.",
            True),
    Setting(594, "retail_persona_modelling", GROUP_BEHAVIORAL,
            "Build retail shopper personas for targeted communications.", True),
    Setting(595, "dynamic_content_personalisation", GROUP_BEHAVIORAL,
            "Personalise on-site content blocks per visitor segment.", True),
    Setting(596, "gamification_module", GROUP_BEHAVIORAL,
            "Gamify shopping with badges, streaks, and challenges.", False),
    Setting(597, "social_proof_injection", GROUP_BEHAVIORAL,
            "Display real-time social-proof signals (views, purchases).", True),
    Setting(598, "urgency_scarcity_engine", GROUP_BEHAVIORAL,
            "Surface urgency/scarcity messaging based on stock levels.", True),
    Setting(599, "opt_out_management", GROUP_BEHAVIORAL,
            "Honour opt-out preferences across all behavioural channels.",
            True),
    Setting(600, "behavioural_audit_log", GROUP_BEHAVIORAL,
            "Maintain tamper-evident audit log of all behavioural events.",
            True),
]

# ---------------------------------------------------------------------------
# Master registry
# ---------------------------------------------------------------------------

DISCOUNT_DOMINATOR_SETTINGS: Dict[int, Setting] = {
    s.id: s
    for s in _ANALYTICS + _INSTORE + _ONLINE + _ENTERPRISE + _BEHAVIORAL
}

SETTINGS_BY_GROUP: Dict[str, list[Setting]] = {
    GROUP_ANALYTICS: _ANALYTICS,
    GROUP_INSTORE: _INSTORE,
    GROUP_ONLINE: _ONLINE,
    GROUP_ENTERPRISE: _ENTERPRISE,
    GROUP_BEHAVIORAL: _BEHAVIORAL,
}

ALL_GROUPS = [
    GROUP_ANALYTICS,
    GROUP_INSTORE,
    GROUP_ONLINE,
    GROUP_ENTERPRISE,
    GROUP_BEHAVIORAL,
]


def get_setting(setting_id: int) -> Setting:
    """Return the :class:`Setting` for the given ID (401–600).

    Raises
    ------
    KeyError
        If *setting_id* is not in the valid range.
    """
    if setting_id not in DISCOUNT_DOMINATOR_SETTINGS:
        raise KeyError(
            f"Setting {setting_id} not found. "
            "Valid range is 401–600."
        )
    return DISCOUNT_DOMINATOR_SETTINGS[setting_id]


def apply_settings(overrides: Dict[int, Any]) -> None:
    """Apply a dictionary of ``{setting_id: value}`` overrides.

    Unknown setting IDs are silently ignored so that partial override
    dictionaries are safe to pass.
    """
    for setting_id, value in overrides.items():
        if setting_id in DISCOUNT_DOMINATOR_SETTINGS:
            DISCOUNT_DOMINATOR_SETTINGS[setting_id].value = value


def get_group_settings(group: str) -> list[Setting]:
    """Return all settings for the given group name.

    Raises
    ------
    KeyError
        If *group* is not a recognised group name.
    """
    if group not in SETTINGS_BY_GROUP:
        raise KeyError(
            f"Unknown group '{group}'. "
            f"Valid groups: {ALL_GROUPS}"
        )
    return SETTINGS_BY_GROUP[group]


def reset_all() -> None:
    """Reset all settings to their default values."""
    for s in DISCOUNT_DOMINATOR_SETTINGS.values():
        s.reset()


def as_dict(group: Optional[str] = None) -> Dict[int, Any]:
    """Return a ``{setting_id: current_value}`` dictionary.

    Parameters
    ----------
    group:
        When provided, only settings from this group are returned.
    """
    if group is not None:
        settings = get_group_settings(group)
    else:
        settings = list(DISCOUNT_DOMINATOR_SETTINGS.values())
    return {s.id: s.value for s in settings}
