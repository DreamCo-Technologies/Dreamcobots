"""
Database module for the SaaS Selling Bot.
Manages a SQLite database of 200 free SaaS tools with categories,
pricing, descriptions, API details, and affiliate links.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "saas_tools.db")

# ─────────────────────────────────────────────────────────────
# 200 free SaaS tools across 6 categories
# ─────────────────────────────────────────────────────────────
SAAS_TOOLS = [
    # ── ANALYTICS (1-35) ──────────────────────────────────────
    {"name": "Google Analytics", "category": "Analytics", "description": "Web analytics service that tracks website traffic and user behaviour.", "api_url": "https://developers.google.com/analytics", "pricing": "Free", "affiliate_link": "https://analytics.google.com", "docs_url": "https://developers.google.com/analytics/devguides"},
    {"name": "Mixpanel", "category": "Analytics", "description": "Product analytics platform for tracking user interactions with web/mobile apps.", "api_url": "https://developer.mixpanel.com/reference/overview", "pricing": "Free tier – 100k events/month", "affiliate_link": "https://mixpanel.com", "docs_url": "https://developer.mixpanel.com"},
    {"name": "Amplitude", "category": "Analytics", "description": "Digital analytics platform for behavioural analytics and event tracking.", "api_url": "https://www.docs.developers.amplitude.com", "pricing": "Free tier – unlimited events", "affiliate_link": "https://amplitude.com", "docs_url": "https://www.docs.developers.amplitude.com"},
    {"name": "Heap", "category": "Analytics", "description": "Automatically captures every user action without requiring manual instrumentation.", "api_url": "https://docs.heap.io/reference/getting-started-with-heap-apis", "pricing": "Free tier – 10k sessions/month", "affiliate_link": "https://heap.io", "docs_url": "https://docs.heap.io"},
    {"name": "Hotjar", "category": "Analytics", "description": "Heatmaps, session recordings, and feedback tools for website optimisation.", "api_url": "https://api.hotjar.com", "pricing": "Free tier – 1050 sessions/month", "affiliate_link": "https://hotjar.com", "docs_url": "https://help.hotjar.com/hc/en-us/categories/115001307791"},
    {"name": "Clicky", "category": "Analytics", "description": "Real-time web analytics with heatmaps and uptime monitoring.", "api_url": "https://clicky.com/api", "pricing": "Free – 1 site / 3000 daily pageviews", "affiliate_link": "https://clicky.com", "docs_url": "https://clicky.com/api"},
    {"name": "Matomo", "category": "Analytics", "description": "Open-source analytics platform with full data ownership.", "api_url": "https://developer.matomo.org/api-reference/reporting-api", "pricing": "Free self-hosted", "affiliate_link": "https://matomo.org", "docs_url": "https://developer.matomo.org"},
    {"name": "Plausible", "category": "Analytics", "description": "Lightweight, privacy-friendly Google Analytics alternative.", "api_url": "https://plausible.io/docs/stats-api", "pricing": "Free 30-day trial; self-host free", "affiliate_link": "https://plausible.io", "docs_url": "https://plausible.io/docs"},
    {"name": "PostHog", "category": "Analytics", "description": "Open-source product analytics, feature flags, and session recordings.", "api_url": "https://posthog.com/docs/api", "pricing": "Free – 1M events/month", "affiliate_link": "https://posthog.com", "docs_url": "https://posthog.com/docs"},
    {"name": "Countly", "category": "Analytics", "description": "Mobile and web analytics platform with SDKs for 18+ platforms.", "api_url": "https://api.count.ly", "pricing": "Free community edition", "affiliate_link": "https://count.ly", "docs_url": "https://support.count.ly"},
    {"name": "Open Web Analytics", "category": "Analytics", "description": "Open-source web analytics framework that uses PHP and MySQL.", "api_url": "https://github.com/padams/Open-Web-Analytics", "pricing": "Free self-hosted", "affiliate_link": "https://www.openwebanalytics.com", "docs_url": "https://github.com/padams/Open-Web-Analytics/wiki"},
    {"name": "Umami", "category": "Analytics", "description": "Simple, fast, privacy-focused web analytics self-hosted alternative.", "api_url": "https://umami.is/docs/api", "pricing": "Free self-hosted", "affiliate_link": "https://umami.is", "docs_url": "https://umami.is/docs"},
    {"name": "Fathom Analytics", "category": "Analytics", "description": "Simple, privacy-focused website analytics that respects GDPR.", "api_url": "https://usefathom.com/api", "pricing": "Free 7-day trial", "affiliate_link": "https://usefathom.com", "docs_url": "https://usefathom.com/docs"},
    {"name": "Segment", "category": "Analytics", "description": "Customer data platform that collects, cleans, and routes data to 300+ tools.", "api_url": "https://segment.com/docs/connections/sources/catalog/libraries/server/http-api/", "pricing": "Free – 1000 MTUs/month", "affiliate_link": "https://segment.com", "docs_url": "https://segment.com/docs"},
    {"name": "Keen.io", "category": "Analytics", "description": "Event data collection and analytics API platform.", "api_url": "https://keen.io/docs/api/", "pricing": "Free – 50k events/month", "affiliate_link": "https://keen.io", "docs_url": "https://keen.io/docs"},
    {"name": "Chartbeat", "category": "Analytics", "description": "Real-time content analytics for digital publishers.", "api_url": "https://chartbeat.com/publishing/api/", "pricing": "Free trial", "affiliate_link": "https://chartbeat.com", "docs_url": "https://chartbeat.com/docs/api"},
    {"name": "Woopra", "category": "Analytics", "description": "Customer journey analytics platform unifying data across touchpoints.", "api_url": "https://www.woopra.com/docs/developer/", "pricing": "Free – 500k actions/month", "affiliate_link": "https://woopra.com", "docs_url": "https://www.woopra.com/docs"},
    {"name": "Ackee", "category": "Analytics", "description": "Self-hosted, privacy-focused analytics tool built with Node.js.", "api_url": "https://docs.ackee.electerious.com/#/docs/API", "pricing": "Free self-hosted", "affiliate_link": "https://ackee.electerious.com", "docs_url": "https://docs.ackee.electerious.com"},
    {"name": "Smartlook", "category": "Analytics", "description": "Qualitative analytics with session recordings and event tracking.", "api_url": "https://web.smartlook.com/docs/sdk/smartlook-api", "pricing": "Free – 3k sessions/month", "affiliate_link": "https://smartlook.com", "docs_url": "https://web.smartlook.com/docs"},
    {"name": "Metabase", "category": "Analytics", "description": "Open-source BI tool for querying databases and visualising data.", "api_url": "https://www.metabase.com/docs/latest/api-documentation.html", "pricing": "Free self-hosted", "affiliate_link": "https://metabase.com", "docs_url": "https://www.metabase.com/docs/latest"},
    {"name": "Grafana", "category": "Analytics", "description": "Open-source observability and data visualisation platform.", "api_url": "https://grafana.com/docs/grafana/latest/http_api/", "pricing": "Free cloud tier", "affiliate_link": "https://grafana.com", "docs_url": "https://grafana.com/docs"},
    {"name": "Kibana", "category": "Analytics", "description": "Data visualisation dashboard for Elasticsearch data.", "api_url": "https://www.elastic.co/guide/en/kibana/current/api.html", "pricing": "Free open-source", "affiliate_link": "https://www.elastic.co/kibana", "docs_url": "https://www.elastic.co/guide/en/kibana/current"},
    {"name": "Redash", "category": "Analytics", "description": "Open-source BI tool for connecting and querying data sources.", "api_url": "https://redash.io/help/open-source/admin-guide/api-key-authentication", "pricing": "Free self-hosted", "affiliate_link": "https://redash.io", "docs_url": "https://redash.io/help"},
    {"name": "Superset", "category": "Analytics", "description": "Apache Superset – modern open-source data exploration and visualisation platform.", "api_url": "https://superset.apache.org/docs/api", "pricing": "Free open-source", "affiliate_link": "https://superset.apache.org", "docs_url": "https://superset.apache.org/docs"},
    {"name": "Looker Studio", "category": "Analytics", "description": "Free Google tool to turn data into informative, customisable dashboards.", "api_url": "https://developers.google.com/looker-studio", "pricing": "Free", "affiliate_link": "https://lookerstudio.google.com", "docs_url": "https://developers.google.com/looker-studio"},
    {"name": "Datadog (Free)", "category": "Analytics", "description": "Monitoring and analytics platform – free tier for infrastructure metrics.", "api_url": "https://docs.datadoghq.com/api/latest/", "pricing": "Free – 5 hosts", "affiliate_link": "https://datadoghq.com", "docs_url": "https://docs.datadoghq.com"},
    {"name": "New Relic (Free)", "category": "Analytics", "description": "Full-stack observability platform with APM, logs, and dashboards.", "api_url": "https://docs.newrelic.com/docs/apis/intro-apis/introduction-new-relic-apis/", "pricing": "Free – 100 GB/month ingest", "affiliate_link": "https://newrelic.com", "docs_url": "https://docs.newrelic.com"},
    {"name": "Sentry (Free)", "category": "Analytics", "description": "Application monitoring and error tracking platform.", "api_url": "https://docs.sentry.io/api/", "pricing": "Free – 5k errors/month", "affiliate_link": "https://sentry.io", "docs_url": "https://docs.sentry.io"},
    {"name": "Bugsnag (Free)", "category": "Analytics", "description": "Application stability monitoring and error reporting.", "api_url": "https://bugsnagapiv2.docs.apiary.io", "pricing": "Free – 7500 events/month", "affiliate_link": "https://www.bugsnag.com", "docs_url": "https://docs.bugsnag.com"},
    {"name": "Rollbar (Free)", "category": "Analytics", "description": "Real-time error tracking and debugging platform for developers.", "api_url": "https://docs.rollbar.com/reference/", "pricing": "Free – 5k events/month", "affiliate_link": "https://rollbar.com", "docs_url": "https://docs.rollbar.com"},
    {"name": "LogRocket (Free)", "category": "Analytics", "description": "Frontend monitoring with session replay and performance tracking.", "api_url": "https://docs.logrocket.com/reference", "pricing": "Free – 1000 sessions/month", "affiliate_link": "https://logrocket.com", "docs_url": "https://docs.logrocket.com"},
    {"name": "FullStory (Free)", "category": "Analytics", "description": "Digital experience intelligence platform with session recordings.", "api_url": "https://developer.fullstory.com/server/v2/events/create-events/", "pricing": "Free – 1000 sessions/month", "affiliate_link": "https://fullstory.com", "docs_url": "https://developer.fullstory.com"},
    {"name": "Mouseflow (Free)", "category": "Analytics", "description": "Session replay, heatmaps, funnels, forms, and feedback surveys.", "api_url": "https://api.mouseflow.com", "pricing": "Free – 500 recordings/month", "affiliate_link": "https://mouseflow.com", "docs_url": "https://help.mouseflow.com"},
    {"name": "Piwik PRO (Free)", "category": "Analytics", "description": "Privacy-focused analytics suite with tag manager and consent management.", "api_url": "https://developers.piwik.pro/", "pricing": "Free – 500k actions/month", "affiliate_link": "https://piwik.pro", "docs_url": "https://help.piwik.pro"},
    {"name": "Inspectlet (Free)", "category": "Analytics", "description": "Session recording, heatmaps, and form analytics for websites.", "api_url": "https://www.inspectlet.com/docs/api", "pricing": "Free – 100 recordings/month", "affiliate_link": "https://inspectlet.com", "docs_url": "https://www.inspectlet.com/docs"},

    # ── MARKETING AUTOMATION (36-70) ──────────────────────────
    {"name": "Mailchimp", "category": "Marketing", "description": "Email marketing and marketing automation platform.", "api_url": "https://mailchimp.com/developer/marketing/api/", "pricing": "Free – 500 contacts / 1k emails/month", "affiliate_link": "https://mailchimp.com", "docs_url": "https://mailchimp.com/developer"},
    {"name": "HubSpot (Free)", "category": "Marketing", "description": "CRM, marketing, sales, and customer service platform.", "api_url": "https://developers.hubspot.com/docs/api/overview", "pricing": "Free CRM tier", "affiliate_link": "https://hubspot.com", "docs_url": "https://developers.hubspot.com"},
    {"name": "Brevo (Sendinblue)", "category": "Marketing", "description": "Email, SMS, and marketing automation platform.", "api_url": "https://developers.brevo.com/", "pricing": "Free – 300 emails/day", "affiliate_link": "https://brevo.com", "docs_url": "https://developers.brevo.com"},
    {"name": "Mailjet", "category": "Marketing", "description": "Email delivery and marketing platform for developers and marketers.", "api_url": "https://dev.mailjet.com/", "pricing": "Free – 200 emails/day", "affiliate_link": "https://mailjet.com", "docs_url": "https://dev.mailjet.com"},
    {"name": "Moosend", "category": "Marketing", "description": "Email marketing and automation with advanced segmentation.", "api_url": "https://moosend.com/blog/moosend-api/", "pricing": "Free – 1000 subscribers", "affiliate_link": "https://moosend.com", "docs_url": "https://moosend.com/blog/moosend-api"},
    {"name": "EmailOctopus", "category": "Marketing", "description": "Simple and affordable email marketing platform.", "api_url": "https://emailoctopus.com/api-documentation", "pricing": "Free – 2500 subscribers / 10k emails/month", "affiliate_link": "https://emailoctopus.com", "docs_url": "https://emailoctopus.com/api-documentation"},
    {"name": "Omnisend", "category": "Marketing", "description": "Omnichannel marketing automation for e-commerce.", "api_url": "https://api-docs.omnisend.com/", "pricing": "Free – 500 contacts / 500 emails/month", "affiliate_link": "https://omnisend.com", "docs_url": "https://api-docs.omnisend.com"},
    {"name": "GetResponse (Free)", "category": "Marketing", "description": "Email marketing, landing pages, and marketing automation.", "api_url": "https://apidocs.getresponse.com/v3", "pricing": "Free – 500 contacts", "affiliate_link": "https://getresponse.com", "docs_url": "https://apidocs.getresponse.com"},
    {"name": "Benchmark Email", "category": "Marketing", "description": "Email marketing platform with drag-and-drop email builder.", "api_url": "https://kb.benchmarkemail.com/developers/api/", "pricing": "Free – 500 subscribers / 3500 emails/month", "affiliate_link": "https://benchmarkemail.com", "docs_url": "https://kb.benchmarkemail.com/developers"},
    {"name": "MailerLite", "category": "Marketing", "description": "Email marketing software with automation and landing pages.", "api_url": "https://developers.mailerlite.com/", "pricing": "Free – 1000 subscribers / 12k emails/month", "affiliate_link": "https://mailerlite.com", "docs_url": "https://developers.mailerlite.com"},
    {"name": "Klaviyo (Free)", "category": "Marketing", "description": "Marketing automation platform focused on e-commerce email and SMS.", "api_url": "https://developers.klaviyo.com/en/reference/api-overview", "pricing": "Free – 250 contacts", "affiliate_link": "https://klaviyo.com", "docs_url": "https://developers.klaviyo.com"},
    {"name": "ActiveCampaign (Free)", "category": "Marketing", "description": "Customer experience automation with email marketing and CRM.", "api_url": "https://developers.activecampaign.com/reference/overview", "pricing": "Free 14-day trial", "affiliate_link": "https://activecampaign.com", "docs_url": "https://developers.activecampaign.com"},
    {"name": "Buffer (Free)", "category": "Marketing", "description": "Social media management platform for scheduling and analytics.", "api_url": "https://buffer.com/developers/api", "pricing": "Free – 3 channels", "affiliate_link": "https://buffer.com", "docs_url": "https://buffer.com/developers/api"},
    {"name": "Hootsuite (Free)", "category": "Marketing", "description": "Social media management tool for scheduling and monitoring.", "api_url": "https://developer.hootsuite.com/", "pricing": "Free – 2 social accounts", "affiliate_link": "https://hootsuite.com", "docs_url": "https://developer.hootsuite.com"},
    {"name": "Later (Free)", "category": "Marketing", "description": "Social media scheduling tool focused on visual content.", "api_url": "https://later.com/blog/social-media-api/", "pricing": "Free – 14 posts/profile/month", "affiliate_link": "https://later.com", "docs_url": "https://help.later.com"},
    {"name": "Sprout Social (Free)", "category": "Marketing", "description": "Social media management and analytics platform.", "api_url": "https://developers.sproutsocial.com/", "pricing": "Free 30-day trial", "affiliate_link": "https://sproutsocial.com", "docs_url": "https://developers.sproutsocial.com"},
    {"name": "Zoho Campaigns (Free)", "category": "Marketing", "description": "Email marketing software integrated with Zoho CRM.", "api_url": "https://www.zoho.com/campaigns/help/api/", "pricing": "Free – 2000 contacts / 6000 emails/month", "affiliate_link": "https://campaigns.zoho.com", "docs_url": "https://www.zoho.com/campaigns/help/api"},
    {"name": "Twilio (Free)", "category": "Marketing", "description": "Cloud communications platform for SMS, voice, email, and messaging.", "api_url": "https://www.twilio.com/docs/usage/api", "pricing": "Free – $15 trial credit", "affiliate_link": "https://twilio.com", "docs_url": "https://www.twilio.com/docs"},
    {"name": "SendGrid (Free)", "category": "Marketing", "description": "Cloud-based email delivery service for transactional email.", "api_url": "https://docs.sendgrid.com/api-reference/", "pricing": "Free – 100 emails/day", "affiliate_link": "https://sendgrid.com", "docs_url": "https://docs.sendgrid.com"},
    {"name": "ConvertKit (Free)", "category": "Marketing", "description": "Email marketing for creators with automation and landing pages.", "api_url": "https://developers.convertkit.com/", "pricing": "Free – 300 subscribers", "affiliate_link": "https://convertkit.com", "docs_url": "https://developers.convertkit.com"},
    {"name": "Drip (Free)", "category": "Marketing", "description": "E-commerce CRM and email marketing automation platform.", "api_url": "https://developer.drip.com/", "pricing": "Free 14-day trial", "affiliate_link": "https://drip.com", "docs_url": "https://developer.drip.com"},
    {"name": "Ontraport (Free)", "category": "Marketing", "description": "All-in-one business automation software for CRM and email marketing.", "api_url": "https://api.ontraport.com/", "pricing": "Free 14-day trial", "affiliate_link": "https://ontraport.com", "docs_url": "https://api.ontraport.com"},
    {"name": "Autopilot (Free)", "category": "Marketing", "description": "Marketing automation platform for visual customer journeys.", "api_url": "https://autopilothq.com/api/", "pricing": "Free 30-day trial", "affiliate_link": "https://autopilothq.com", "docs_url": "https://autopilothq.com/api"},
    {"name": "Marketo (Free)", "category": "Marketing", "description": "B2B marketing automation platform by Adobe.", "api_url": "https://developers.marketo.com/rest-api/", "pricing": "Free trial", "affiliate_link": "https://marketo.com", "docs_url": "https://developers.marketo.com"},
    {"name": "Pardot (Free)", "category": "Marketing", "description": "B2B marketing automation by Salesforce.", "api_url": "https://developer.salesforce.com/docs/marketing/pardot/overview", "pricing": "Free trial", "affiliate_link": "https://pardot.com", "docs_url": "https://developer.salesforce.com/docs/marketing/pardot"},
    {"name": "Intercom (Free)", "category": "Marketing", "description": "Customer communications platform with live chat and targeted messaging.", "api_url": "https://developers.intercom.com/", "pricing": "Free – 1 seat", "affiliate_link": "https://intercom.com", "docs_url": "https://developers.intercom.com"},
    {"name": "Drift (Free)", "category": "Marketing", "description": "Conversational marketing platform with live chat and chatbots.", "api_url": "https://devdocs.drift.com/docs", "pricing": "Free – 1 seat", "affiliate_link": "https://drift.com", "docs_url": "https://devdocs.drift.com"},
    {"name": "Crisp (Free)", "category": "Marketing", "description": "Customer messaging platform with chatbot and live chat.", "api_url": "https://docs.crisp.chat/references/rest-api/v1/", "pricing": "Free – 2 agents", "affiliate_link": "https://crisp.chat", "docs_url": "https://docs.crisp.chat"},
    {"name": "Tidio (Free)", "category": "Marketing", "description": "Live chat and chatbot platform for customer support and sales.", "api_url": "https://www.tidio.com/page/api/", "pricing": "Free – 50 conversations/month", "affiliate_link": "https://tidio.com", "docs_url": "https://www.tidio.com/page/api"},
    {"name": "Tawk.to", "category": "Marketing", "description": "Free live chat and customer monitoring platform.", "api_url": "https://developer.tawk.to/", "pricing": "Free forever", "affiliate_link": "https://tawk.to", "docs_url": "https://developer.tawk.to"},
    {"name": "Freshdesk (Free)", "category": "Marketing", "description": "Customer support helpdesk software with ticketing and automation.", "api_url": "https://developers.freshdesk.com/api/", "pricing": "Free – 10 agents", "affiliate_link": "https://freshdesk.com", "docs_url": "https://developers.freshdesk.com"},
    {"name": "Zendesk (Free)", "category": "Marketing", "description": "Customer service platform with ticketing and live chat.", "api_url": "https://developer.zendesk.com/api-reference/", "pricing": "Free trial", "affiliate_link": "https://zendesk.com", "docs_url": "https://developer.zendesk.com"},
    {"name": "Hubspot Forms", "category": "Marketing", "description": "Free form builder integrated with HubSpot CRM.", "api_url": "https://developers.hubspot.com/docs/api/marketing/forms", "pricing": "Free", "affiliate_link": "https://hubspot.com/products/marketing/forms", "docs_url": "https://developers.hubspot.com/docs/api/marketing/forms"},
    {"name": "Typeform (Free)", "category": "Marketing", "description": "Interactive form and survey builder with conversational design.", "api_url": "https://developer.typeform.com/", "pricing": "Free – 10 responses/month", "affiliate_link": "https://typeform.com", "docs_url": "https://developer.typeform.com"},
    {"name": "SurveyMonkey (Free)", "category": "Marketing", "description": "Online survey tool for collecting data and feedback.", "api_url": "https://developer.surveymonkey.com/api/v3/", "pricing": "Free – 10 questions / 40 responses", "affiliate_link": "https://surveymonkey.com", "docs_url": "https://developer.surveymonkey.com"},

    # ── DEVELOPMENT (71-105) ──────────────────────────────────
    {"name": "GitHub", "category": "Development", "description": "Code hosting platform for version control and collaborative development.", "api_url": "https://docs.github.com/en/rest", "pricing": "Free – public/private repos", "affiliate_link": "https://github.com", "docs_url": "https://docs.github.com"},
    {"name": "GitLab (Free)", "category": "Development", "description": "Open-source DevOps platform with Git repository management.", "api_url": "https://docs.gitlab.com/ee/api/", "pricing": "Free tier", "affiliate_link": "https://gitlab.com", "docs_url": "https://docs.gitlab.com"},
    {"name": "Bitbucket (Free)", "category": "Development", "description": "Git code hosting with CI/CD pipelines for teams.", "api_url": "https://developer.atlassian.com/server/bitbucket/", "pricing": "Free – 5 users", "affiliate_link": "https://bitbucket.org", "docs_url": "https://developer.atlassian.com/cloud/bitbucket"},
    {"name": "Vercel (Free)", "category": "Development", "description": "Frontend deployment platform optimised for React/Next.js apps.", "api_url": "https://vercel.com/docs/rest-api", "pricing": "Free hobby tier", "affiliate_link": "https://vercel.com", "docs_url": "https://vercel.com/docs"},
    {"name": "Netlify (Free)", "category": "Development", "description": "Web hosting and automation for modern web projects.", "api_url": "https://open-api.netlify.com/", "pricing": "Free – 100 GB bandwidth", "affiliate_link": "https://netlify.com", "docs_url": "https://docs.netlify.com"},
    {"name": "Heroku (Free)", "category": "Development", "description": "Cloud application platform for deploying and scaling apps.", "api_url": "https://devcenter.heroku.com/categories/platform-api", "pricing": "Free eco dynos", "affiliate_link": "https://heroku.com", "docs_url": "https://devcenter.heroku.com"},
    {"name": "Railway (Free)", "category": "Development", "description": "Infrastructure platform to deploy apps and databases with ease.", "api_url": "https://docs.railway.app/reference/public-api", "pricing": "Free – $5 credit/month", "affiliate_link": "https://railway.app", "docs_url": "https://docs.railway.app"},
    {"name": "Render (Free)", "category": "Development", "description": "Unified cloud platform for building and running all your apps.", "api_url": "https://render.com/docs/api", "pricing": "Free static sites and services", "affiliate_link": "https://render.com", "docs_url": "https://render.com/docs"},
    {"name": "Supabase (Free)", "category": "Development", "description": "Open-source Firebase alternative with Postgres database.", "api_url": "https://supabase.com/docs/reference/api", "pricing": "Free – 2 projects", "affiliate_link": "https://supabase.com", "docs_url": "https://supabase.com/docs"},
    {"name": "Firebase (Free)", "category": "Development", "description": "Google's app development platform with database, auth, and hosting.", "api_url": "https://firebase.google.com/docs/reference/rest/database", "pricing": "Free spark plan", "affiliate_link": "https://firebase.google.com", "docs_url": "https://firebase.google.com/docs"},
    {"name": "PlanetScale (Free)", "category": "Development", "description": "MySQL-compatible serverless database platform.", "api_url": "https://planetscale.com/docs/concepts/planetscale-api-overview", "pricing": "Free – 1 database", "affiliate_link": "https://planetscale.com", "docs_url": "https://planetscale.com/docs"},
    {"name": "Neon (Free)", "category": "Development", "description": "Serverless Postgres with autoscaling and branching.", "api_url": "https://neon.tech/docs/reference/api-reference", "pricing": "Free – 0.5 GB storage", "affiliate_link": "https://neon.tech", "docs_url": "https://neon.tech/docs"},
    {"name": "MongoDB Atlas (Free)", "category": "Development", "description": "Cloud-hosted MongoDB database service.", "api_url": "https://www.mongodb.com/docs/atlas/api/", "pricing": "Free – 512 MB storage", "affiliate_link": "https://mongodb.com/atlas", "docs_url": "https://www.mongodb.com/docs/atlas"},
    {"name": "Redis Cloud (Free)", "category": "Development", "description": "Managed Redis database service for caching and queuing.", "api_url": "https://redis.com/redis-enterprise/technology/redis-enterprise-api/", "pricing": "Free – 30 MB", "affiliate_link": "https://redis.com/try-free", "docs_url": "https://docs.redis.com"},
    {"name": "Upstash (Free)", "category": "Development", "description": "Serverless Redis and Kafka with HTTP API.", "api_url": "https://docs.upstash.com/redis/features/restapi", "pricing": "Free – 10k commands/day", "affiliate_link": "https://upstash.com", "docs_url": "https://docs.upstash.com"},
    {"name": "Cloudflare Workers (Free)", "category": "Development", "description": "Serverless execution environment at the edge.", "api_url": "https://developers.cloudflare.com/api/", "pricing": "Free – 100k requests/day", "affiliate_link": "https://workers.cloudflare.com", "docs_url": "https://developers.cloudflare.com/workers"},
    {"name": "AWS Lambda (Free)", "category": "Development", "description": "Serverless computing service from Amazon Web Services.", "api_url": "https://docs.aws.amazon.com/lambda/latest/dg/API_Reference.html", "pricing": "Free – 1M requests/month", "affiliate_link": "https://aws.amazon.com/lambda", "docs_url": "https://docs.aws.amazon.com/lambda/latest/dg"},
    {"name": "Google Cloud Functions (Free)", "category": "Development", "description": "Event-driven serverless compute platform by Google.", "api_url": "https://cloud.google.com/functions/docs/reference/rest", "pricing": "Free – 2M invocations/month", "affiliate_link": "https://cloud.google.com/functions", "docs_url": "https://cloud.google.com/functions/docs"},
    {"name": "Azure Functions (Free)", "category": "Development", "description": "Serverless compute service from Microsoft Azure.", "api_url": "https://learn.microsoft.com/en-us/rest/api/appservice/web-apps", "pricing": "Free – 1M executions/month", "affiliate_link": "https://azure.microsoft.com/en-us/services/functions", "docs_url": "https://learn.microsoft.com/en-us/azure/azure-functions"},
    {"name": "Docker Hub (Free)", "category": "Development", "description": "Container image registry for building, shipping, and running apps.", "api_url": "https://docs.docker.com/docker-hub/api/latest/", "pricing": "Free – public repos", "affiliate_link": "https://hub.docker.com", "docs_url": "https://docs.docker.com"},
    {"name": "CircleCI (Free)", "category": "Development", "description": "Continuous integration and delivery platform.", "api_url": "https://circleci.com/docs/api/v2/", "pricing": "Free – 6000 build mins/month", "affiliate_link": "https://circleci.com", "docs_url": "https://circleci.com/docs"},
    {"name": "Travis CI (Free)", "category": "Development", "description": "Hosted continuous integration service for GitHub projects.", "api_url": "https://developer.travis-ci.com/", "pricing": "Free for open-source", "affiliate_link": "https://travis-ci.com", "docs_url": "https://docs.travis-ci.com"},
    {"name": "Jenkins (Free)", "category": "Development", "description": "Open-source automation server for CI/CD pipelines.", "api_url": "https://www.jenkins.io/doc/book/using/remote-access-api/", "pricing": "Free open-source", "affiliate_link": "https://jenkins.io", "docs_url": "https://www.jenkins.io/doc"},
    {"name": "SonarCloud (Free)", "category": "Development", "description": "Cloud-based code quality and security analysis service.", "api_url": "https://sonarcloud.io/web_api", "pricing": "Free for open-source", "affiliate_link": "https://sonarcloud.io", "docs_url": "https://docs.sonarcloud.io"},
    {"name": "Snyk (Free)", "category": "Development", "description": "Developer security platform for finding and fixing vulnerabilities.", "api_url": "https://snyk.docs.apiary.io/", "pricing": "Free – 200 tests/month", "affiliate_link": "https://snyk.io", "docs_url": "https://docs.snyk.io"},
    {"name": "Postman (Free)", "category": "Development", "description": "API development and testing platform.", "api_url": "https://www.postman.com/postman/workspace/postman-public-workspace/collection/", "pricing": "Free – 3 users", "affiliate_link": "https://postman.com", "docs_url": "https://learning.postman.com/docs"},
    {"name": "Swagger (Free)", "category": "Development", "description": "Open-source API documentation and design tools.", "api_url": "https://swagger.io/specification/", "pricing": "Free open-source", "affiliate_link": "https://swagger.io", "docs_url": "https://swagger.io/docs"},
    {"name": "Apiary (Free)", "category": "Development", "description": "API design, documentation, and testing platform.", "api_url": "https://apiary.io", "pricing": "Free – 1 API", "affiliate_link": "https://apiary.io", "docs_url": "https://help.apiary.io"},
    {"name": "RapidAPI (Free)", "category": "Development", "description": "API marketplace and management platform.", "api_url": "https://docs.rapidapi.com/docs/api", "pricing": "Free tier available", "affiliate_link": "https://rapidapi.com", "docs_url": "https://docs.rapidapi.com"},
    {"name": "Ngrok (Free)", "category": "Development", "description": "Secure tunnels to localhost for testing webhooks and APIs.", "api_url": "https://ngrok.com/docs/api/", "pricing": "Free – 1 tunnel", "affiliate_link": "https://ngrok.com", "docs_url": "https://ngrok.com/docs"},
    {"name": "Localtunnel", "category": "Development", "description": "Free service to expose a local server to the internet.", "api_url": "https://github.com/localtunnel/localtunnel", "pricing": "Free open-source", "affiliate_link": "https://localtunnel.github.io/www/", "docs_url": "https://github.com/localtunnel/localtunnel"},
    {"name": "Pipedream (Free)", "category": "Development", "description": "Integration platform for building workflows and automations.", "api_url": "https://pipedream.com/docs/api/rest/", "pricing": "Free – 100 credits/day", "affiliate_link": "https://pipedream.com", "docs_url": "https://pipedream.com/docs"},
    {"name": "Zapier (Free)", "category": "Development", "description": "No-code automation tool connecting 5000+ apps.", "api_url": "https://zapier.com/developer/documentation/v2/general/", "pricing": "Free – 100 tasks/month", "affiliate_link": "https://zapier.com", "docs_url": "https://zapier.com/developer/documentation"},
    {"name": "Make (Integromat) Free", "category": "Development", "description": "Visual automation platform for connecting apps and services.", "api_url": "https://www.make.com/en/api-documentation", "pricing": "Free – 1000 ops/month", "affiliate_link": "https://make.com", "docs_url": "https://www.make.com/en/help"},
    {"name": "n8n (Free)", "category": "Development", "description": "Open-source workflow automation tool.", "api_url": "https://docs.n8n.io/api/", "pricing": "Free self-hosted", "affiliate_link": "https://n8n.io", "docs_url": "https://docs.n8n.io"},

    # ── COLLABORATION (106-140) ───────────────────────────────
    {"name": "Slack (Free)", "category": "Collaboration", "description": "Business communication platform with channels and integrations.", "api_url": "https://api.slack.com/", "pricing": "Free – 10k messages", "affiliate_link": "https://slack.com", "docs_url": "https://api.slack.com/docs"},
    {"name": "Microsoft Teams (Free)", "category": "Collaboration", "description": "Chat, video, and collaboration hub by Microsoft.", "api_url": "https://learn.microsoft.com/en-us/graph/teams-concept-overview", "pricing": "Free tier", "affiliate_link": "https://teams.microsoft.com", "docs_url": "https://learn.microsoft.com/en-us/microsoftteams"},
    {"name": "Discord (Free)", "category": "Collaboration", "description": "Voice, video, and text communication platform.", "api_url": "https://discord.com/developers/docs/intro", "pricing": "Free", "affiliate_link": "https://discord.com", "docs_url": "https://discord.com/developers/docs"},
    {"name": "Trello (Free)", "category": "Collaboration", "description": "Kanban-style project management and task tracking tool.", "api_url": "https://developer.atlassian.com/cloud/trello/rest/", "pricing": "Free – unlimited cards", "affiliate_link": "https://trello.com", "docs_url": "https://developer.atlassian.com/cloud/trello"},
    {"name": "Asana (Free)", "category": "Collaboration", "description": "Work management platform for teams to organise tasks and projects.", "api_url": "https://developers.asana.com/reference/rest-api-reference", "pricing": "Free – 15 members", "affiliate_link": "https://asana.com", "docs_url": "https://developers.asana.com"},
    {"name": "Notion (Free)", "category": "Collaboration", "description": "All-in-one workspace for notes, docs, databases, and project management.", "api_url": "https://developers.notion.com/", "pricing": "Free – unlimited blocks", "affiliate_link": "https://notion.so", "docs_url": "https://developers.notion.com"},
    {"name": "ClickUp (Free)", "category": "Collaboration", "description": "All-in-one project management with tasks, docs, and goals.", "api_url": "https://clickup.com/api/", "pricing": "Free – unlimited tasks", "affiliate_link": "https://clickup.com", "docs_url": "https://clickup.com/api"},
    {"name": "Monday.com (Free)", "category": "Collaboration", "description": "Work OS for project and task management.", "api_url": "https://developer.monday.com/api-reference/docs", "pricing": "Free – 2 seats", "affiliate_link": "https://monday.com", "docs_url": "https://developer.monday.com"},
    {"name": "Jira (Free)", "category": "Collaboration", "description": "Issue and project tracking software for agile teams.", "api_url": "https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/", "pricing": "Free – 10 users", "affiliate_link": "https://atlassian.com/software/jira", "docs_url": "https://developer.atlassian.com/cloud/jira"},
    {"name": "Linear (Free)", "category": "Collaboration", "description": "Issue tracking tool for software teams.", "api_url": "https://developers.linear.app/docs/graphql/working-with-the-graphql-api", "pricing": "Free – 250 issues", "affiliate_link": "https://linear.app", "docs_url": "https://developers.linear.app/docs"},
    {"name": "Basecamp (Free)", "category": "Collaboration", "description": "Project management and team communication platform.", "api_url": "https://github.com/basecamp/bc3-api", "pricing": "Free – 3 projects", "affiliate_link": "https://basecamp.com", "docs_url": "https://github.com/basecamp/bc3-api"},
    {"name": "Airtable (Free)", "category": "Collaboration", "description": "Cloud collaboration service combining spreadsheet and database features.", "api_url": "https://airtable.com/developers/web/api/introduction", "pricing": "Free – 1200 records", "affiliate_link": "https://airtable.com", "docs_url": "https://airtable.com/developers/web/api"},
    {"name": "Confluence (Free)", "category": "Collaboration", "description": "Team wiki and knowledge base by Atlassian.", "api_url": "https://developer.atlassian.com/cloud/confluence/rest/v2/intro/", "pricing": "Free – 10 users", "affiliate_link": "https://atlassian.com/software/confluence", "docs_url": "https://developer.atlassian.com/cloud/confluence"},
    {"name": "Miro (Free)", "category": "Collaboration", "description": "Online whiteboard and visual collaboration platform.", "api_url": "https://developers.miro.com/reference/api-reference", "pricing": "Free – 3 editable boards", "affiliate_link": "https://miro.com", "docs_url": "https://developers.miro.com"},
    {"name": "Figma (Free)", "category": "Collaboration", "description": "Collaborative design and prototyping tool.", "api_url": "https://www.figma.com/developers/api", "pricing": "Free – 3 projects", "affiliate_link": "https://figma.com", "docs_url": "https://www.figma.com/developers/api"},
    {"name": "Zoom (Free)", "category": "Collaboration", "description": "Video conferencing and web meeting platform.", "api_url": "https://marketplace.zoom.us/docs/api-reference/zoom-api/", "pricing": "Free – 40 min meetings", "affiliate_link": "https://zoom.us", "docs_url": "https://marketplace.zoom.us/docs"},
    {"name": "Google Meet (Free)", "category": "Collaboration", "description": "Video calling platform by Google.", "api_url": "https://developers.google.com/meet/api", "pricing": "Free", "affiliate_link": "https://meet.google.com", "docs_url": "https://developers.google.com/meet"},
    {"name": "Calendly (Free)", "category": "Collaboration", "description": "Automated scheduling platform for meetings.", "api_url": "https://developer.calendly.com/api-docs/", "pricing": "Free – 1 event type", "affiliate_link": "https://calendly.com", "docs_url": "https://developer.calendly.com"},
    {"name": "Doodle (Free)", "category": "Collaboration", "description": "Scheduling and meeting coordination tool.", "api_url": "https://doodle.com/api/v2.0/", "pricing": "Free basic polls", "affiliate_link": "https://doodle.com", "docs_url": "https://doodle.com/api/v2.0"},
    {"name": "Loom (Free)", "category": "Collaboration", "description": "Video messaging tool for async communication.", "api_url": "https://dev.loom.com/docs/reference/", "pricing": "Free – 25 videos", "affiliate_link": "https://loom.com", "docs_url": "https://dev.loom.com/docs"},
    {"name": "Dropbox (Free)", "category": "Collaboration", "description": "Cloud file storage and sharing platform.", "api_url": "https://www.dropbox.com/developers/documentation/http/documentation", "pricing": "Free – 2 GB storage", "affiliate_link": "https://dropbox.com", "docs_url": "https://www.dropbox.com/developers/documentation"},
    {"name": "Google Drive (Free)", "category": "Collaboration", "description": "Cloud storage and file sharing by Google.", "api_url": "https://developers.google.com/drive/api/guides/about-sdk", "pricing": "Free – 15 GB storage", "affiliate_link": "https://drive.google.com", "docs_url": "https://developers.google.com/drive"},
    {"name": "OneDrive (Free)", "category": "Collaboration", "description": "Cloud storage and file sharing by Microsoft.", "api_url": "https://learn.microsoft.com/en-us/onedrive/developer/rest-api/", "pricing": "Free – 5 GB storage", "affiliate_link": "https://onedrive.live.com", "docs_url": "https://learn.microsoft.com/en-us/onedrive/developer"},
    {"name": "Box (Free)", "category": "Collaboration", "description": "Cloud content management and file sharing platform.", "api_url": "https://developer.box.com/reference/", "pricing": "Free – 10 GB storage", "affiliate_link": "https://box.com", "docs_url": "https://developer.box.com"},
    {"name": "Coda (Free)", "category": "Collaboration", "description": "Document editor that combines docs, spreadsheets, and apps.", "api_url": "https://coda.io/developers/apis/v1", "pricing": "Free – 3 makers", "affiliate_link": "https://coda.io", "docs_url": "https://coda.io/developers/apis/v1"},
    {"name": "Roam Research (Free)", "category": "Collaboration", "description": "Note-taking tool for networked thought.", "api_url": "https://roamresearch.com/#/app/help/page/0yjxpNVhK", "pricing": "Free 30-day trial", "affiliate_link": "https://roamresearch.com", "docs_url": "https://roamresearch.com/#/app/help"},
    {"name": "Obsidian (Free)", "category": "Collaboration", "description": "Knowledge base tool using Markdown with local storage.", "api_url": "https://github.com/obsidianmd/obsidian-api", "pricing": "Free personal use", "affiliate_link": "https://obsidian.md", "docs_url": "https://help.obsidian.md"},
    {"name": "Quip (Free)", "category": "Collaboration", "description": "Collaborative word processor for team documents.", "api_url": "https://quip.com/dev/automation/documentation/", "pricing": "Free trial", "affiliate_link": "https://quip.com", "docs_url": "https://quip.com/dev/automation/documentation"},
    {"name": "Taskade (Free)", "category": "Collaboration", "description": "All-in-one collaboration platform with tasks, notes, and video.", "api_url": "https://www.taskade.com/developer", "pricing": "Free – 5 projects", "affiliate_link": "https://taskade.com", "docs_url": "https://www.taskade.com/developer"},
    {"name": "Hive (Free)", "category": "Collaboration", "description": "Project management platform with analytics and time tracking.", "api_url": "https://developers.hive.com/reference", "pricing": "Free – unlimited tasks", "affiliate_link": "https://hive.com", "docs_url": "https://developers.hive.com"},
    {"name": "Wrike (Free)", "category": "Collaboration", "description": "Work management platform for enterprise-level project planning.", "api_url": "https://developers.wrike.com/api/v4/", "pricing": "Free – 5 users", "affiliate_link": "https://wrike.com", "docs_url": "https://developers.wrike.com"},
    {"name": "Todoist (Free)", "category": "Collaboration", "description": "Task management app for personal and team productivity.", "api_url": "https://developer.todoist.com/rest/v2/", "pricing": "Free – 5 active projects", "affiliate_link": "https://todoist.com", "docs_url": "https://developer.todoist.com"},
    {"name": "Any.do (Free)", "category": "Collaboration", "description": "Task management and to-do list app.", "api_url": "https://share.any.do/api/", "pricing": "Free basic plan", "affiliate_link": "https://any.do", "docs_url": "https://any.do"},
    {"name": "Toggl Track (Free)", "category": "Collaboration", "description": "Time tracking tool for freelancers and teams.", "api_url": "https://developers.track.toggl.com/docs/", "pricing": "Free – unlimited tracking", "affiliate_link": "https://toggl.com/track", "docs_url": "https://developers.track.toggl.com"},
    {"name": "Clockify (Free)", "category": "Collaboration", "description": "Free time tracker and timesheet app.", "api_url": "https://clockify.me/developers-api", "pricing": "Free forever", "affiliate_link": "https://clockify.me", "docs_url": "https://clockify.me/developers-api"},

    # ── FINANCE (141-170) ─────────────────────────────────────
    {"name": "Stripe (Free)", "category": "Finance", "description": "Payment processing platform for online businesses.", "api_url": "https://stripe.com/docs/api", "pricing": "Free – pay per transaction", "affiliate_link": "https://stripe.com", "docs_url": "https://stripe.com/docs"},
    {"name": "PayPal (Free)", "category": "Finance", "description": "Online payment platform for global transactions.", "api_url": "https://developer.paypal.com/api/rest/", "pricing": "Free – transaction fees apply", "affiliate_link": "https://paypal.com", "docs_url": "https://developer.paypal.com/docs"},
    {"name": "Square (Free)", "category": "Finance", "description": "Payment and point-of-sale solutions for businesses.", "api_url": "https://developer.squareup.com/reference/square", "pricing": "Free – transaction fees apply", "affiliate_link": "https://squareup.com", "docs_url": "https://developer.squareup.com/docs"},
    {"name": "Plaid (Free)", "category": "Finance", "description": "Financial data API connecting apps to banks.", "api_url": "https://plaid.com/docs/api/", "pricing": "Free sandbox", "affiliate_link": "https://plaid.com", "docs_url": "https://plaid.com/docs"},
    {"name": "Open Exchange Rates", "category": "Finance", "description": "Currency exchange rates and data API.", "api_url": "https://docs.openexchangerates.org/", "pricing": "Free – 1000 requests/month", "affiliate_link": "https://openexchangerates.org", "docs_url": "https://docs.openexchangerates.org"},
    {"name": "CurrencyLayer (Free)", "category": "Finance", "description": "Real-time and historical exchange rate data API.", "api_url": "https://currencylayer.com/documentation", "pricing": "Free – 100 requests/month", "affiliate_link": "https://currencylayer.com", "docs_url": "https://currencylayer.com/documentation"},
    {"name": "Alpha Vantage (Free)", "category": "Finance", "description": "Stock market and financial data API.", "api_url": "https://www.alphavantage.co/documentation/", "pricing": "Free – 500 requests/day", "affiliate_link": "https://alphavantage.co", "docs_url": "https://www.alphavantage.co/documentation"},
    {"name": "Yahoo Finance API", "category": "Finance", "description": "Stock quotes, historical data, and financial news.", "api_url": "https://finance.yahoo.com/news/", "pricing": "Free public access", "affiliate_link": "https://finance.yahoo.com", "docs_url": "https://finance.yahoo.com"},
    {"name": "CoinGecko (Free)", "category": "Finance", "description": "Cryptocurrency prices, market data, and exchange info.", "api_url": "https://www.coingecko.com/en/api/documentation", "pricing": "Free – 10-30 calls/min", "affiliate_link": "https://coingecko.com", "docs_url": "https://www.coingecko.com/api/documentation"},
    {"name": "CoinMarketCap (Free)", "category": "Finance", "description": "Cryptocurrency market capitalisation and data API.", "api_url": "https://coinmarketcap.com/api/documentation/v1/", "pricing": "Free – 333 calls/day", "affiliate_link": "https://coinmarketcap.com", "docs_url": "https://coinmarketcap.com/api/documentation/v1"},
    {"name": "Brex (Free)", "category": "Finance", "description": "Corporate credit card and spend management for startups.", "api_url": "https://developer.brex.com/", "pricing": "Free", "affiliate_link": "https://brex.com", "docs_url": "https://developer.brex.com"},
    {"name": "Ramp (Free)", "category": "Finance", "description": "Corporate card and expense management platform.", "api_url": "https://docs.ramp.com/developer-guide/api-overview", "pricing": "Free", "affiliate_link": "https://ramp.com", "docs_url": "https://docs.ramp.com"},
    {"name": "Wave Accounting (Free)", "category": "Finance", "description": "Free accounting software for small businesses.", "api_url": "https://developer.waveapps.com/graphql/", "pricing": "Free accounting", "affiliate_link": "https://waveapps.com", "docs_url": "https://developer.waveapps.com"},
    {"name": "FreshBooks (Free)", "category": "Finance", "description": "Cloud accounting and invoicing software.", "api_url": "https://www.freshbooks.com/api/start", "pricing": "Free 30-day trial", "affiliate_link": "https://freshbooks.com", "docs_url": "https://www.freshbooks.com/api"},
    {"name": "QuickBooks (Free)", "category": "Finance", "description": "Accounting software for small and medium businesses.", "api_url": "https://developer.intuit.com/app/developer/qbo/docs/get-started", "pricing": "Free 30-day trial", "affiliate_link": "https://quickbooks.intuit.com", "docs_url": "https://developer.intuit.com"},
    {"name": "Xero (Free)", "category": "Finance", "description": "Cloud accounting software for small businesses.", "api_url": "https://developer.xero.com/documentation/api/accounting/overview", "pricing": "Free 30-day trial", "affiliate_link": "https://xero.com", "docs_url": "https://developer.xero.com"},
    {"name": "Zoho Books (Free)", "category": "Finance", "description": "Online accounting software for managing finances.", "api_url": "https://www.zoho.com/books/api/v3/", "pricing": "Free – 1 user / 1000 invoices", "affiliate_link": "https://zoho.com/books", "docs_url": "https://www.zoho.com/books/api/v3"},
    {"name": "Bench (Free)", "category": "Finance", "description": "Online bookkeeping service for small businesses.", "api_url": "https://bench.co/developers/", "pricing": "Free trial", "affiliate_link": "https://bench.co", "docs_url": "https://bench.co"},
    {"name": "Mercury (Free)", "category": "Finance", "description": "Banking for startups and technology companies.", "api_url": "https://docs.mercury.com/", "pricing": "Free", "affiliate_link": "https://mercury.com", "docs_url": "https://docs.mercury.com"},
    {"name": "Lemon Squeezy (Free)", "category": "Finance", "description": "Merchant of record and payments platform for SaaS.", "api_url": "https://docs.lemonsqueezy.com/api", "pricing": "Free – transaction fees apply", "affiliate_link": "https://lemonsqueezy.com", "docs_url": "https://docs.lemonsqueezy.com"},
    {"name": "Paddle (Free)", "category": "Finance", "description": "Revenue delivery platform for software companies.", "api_url": "https://developer.paddle.com/api-reference/overview", "pricing": "Free – revenue share", "affiliate_link": "https://paddle.com", "docs_url": "https://developer.paddle.com"},
    {"name": "Chargebee (Free)", "category": "Finance", "description": "Subscription billing and revenue management platform.", "api_url": "https://apidocs.chargebee.com/docs/api", "pricing": "Free – $0 until $100k revenue", "affiliate_link": "https://chargebee.com", "docs_url": "https://apidocs.chargebee.com"},
    {"name": "Recurly (Free)", "category": "Finance", "description": "Subscription management and billing platform.", "api_url": "https://developers.recurly.com/api/", "pricing": "Free trial", "affiliate_link": "https://recurly.com", "docs_url": "https://developers.recurly.com"},
    {"name": "Zuora (Free)", "category": "Finance", "description": "Enterprise subscription management and billing platform.", "api_url": "https://developer.zuora.com/api-references/api/overview/", "pricing": "Free trial", "affiliate_link": "https://zuora.com", "docs_url": "https://developer.zuora.com"},
    {"name": "Baremetrics (Free)", "category": "Finance", "description": "SaaS analytics and metrics platform for subscription businesses.", "api_url": "https://developers.baremetrics.com/reference/introduction", "pricing": "Free trial", "affiliate_link": "https://baremetrics.com", "docs_url": "https://developers.baremetrics.com"},
    {"name": "ChartMogul (Free)", "category": "Finance", "description": "Subscription analytics platform for measuring MRR and churn.", "api_url": "https://dev.chartmogul.com/reference", "pricing": "Free – 1000 customers", "affiliate_link": "https://chartmogul.com", "docs_url": "https://dev.chartmogul.com"},
    {"name": "Profitwell (Free)", "category": "Finance", "description": "Subscription financial metrics for SaaS companies.", "api_url": "https://developer.profitwell.com/", "pricing": "Free", "affiliate_link": "https://profitwell.com", "docs_url": "https://developer.profitwell.com"},
    {"name": "Codat (Free)", "category": "Finance", "description": "Universal API for small business financial data.", "api_url": "https://docs.codat.io/codat-api", "pricing": "Free sandbox", "affiliate_link": "https://codat.io", "docs_url": "https://docs.codat.io"},
    {"name": "Finicity (Free)", "category": "Finance", "description": "Open banking data network and financial APIs.", "api_url": "https://developer.finicity.com/", "pricing": "Free sandbox", "affiliate_link": "https://finicity.com", "docs_url": "https://developer.finicity.com"},
    {"name": "Yodlee (Free)", "category": "Finance", "description": "Financial data aggregation and analytics platform.", "api_url": "https://developer.yodlee.com/", "pricing": "Free sandbox", "affiliate_link": "https://yodlee.com", "docs_url": "https://developer.yodlee.com"},

    # ── AI (171-200) ──────────────────────────────────────────
    {"name": "OpenAI API", "category": "AI", "description": "Access GPT-4, DALL-E, Whisper, and other AI models.", "api_url": "https://platform.openai.com/docs/api-reference", "pricing": "Free $5 credit on sign-up", "affiliate_link": "https://platform.openai.com", "docs_url": "https://platform.openai.com/docs"},
    {"name": "Hugging Face (Free)", "category": "AI", "description": "Open-source AI model hub with 200k+ models.", "api_url": "https://huggingface.co/docs/api-inference/index", "pricing": "Free Inference API", "affiliate_link": "https://huggingface.co", "docs_url": "https://huggingface.co/docs"},
    {"name": "Cohere (Free)", "category": "AI", "description": "NLP API for text generation, classification, and embeddings.", "api_url": "https://docs.cohere.com/reference/about", "pricing": "Free trial – 100 calls/min", "affiliate_link": "https://cohere.com", "docs_url": "https://docs.cohere.com"},
    {"name": "Anthropic Claude (Free)", "category": "AI", "description": "AI assistant API from Anthropic for safe, steerable AI.", "api_url": "https://docs.anthropic.com/claude/reference/getting-started-with-the-api", "pricing": "Free $5 credit on sign-up", "affiliate_link": "https://anthropic.com", "docs_url": "https://docs.anthropic.com"},
    {"name": "Google Gemini API", "category": "AI", "description": "Access Google's multimodal Gemini AI models.", "api_url": "https://ai.google.dev/api/rest/v1beta/", "pricing": "Free – 60 requests/min", "affiliate_link": "https://ai.google.dev", "docs_url": "https://ai.google.dev/docs"},
    {"name": "Stability AI (Free)", "category": "AI", "description": "Stable Diffusion image generation API.", "api_url": "https://platform.stability.ai/rest-api", "pricing": "Free – 25 credits", "affiliate_link": "https://stability.ai", "docs_url": "https://platform.stability.ai/docs"},
    {"name": "Replicate (Free)", "category": "AI", "description": "Run open-source ML models via a cloud API.", "api_url": "https://replicate.com/docs/reference/http", "pricing": "Free – pay per run", "affiliate_link": "https://replicate.com", "docs_url": "https://replicate.com/docs"},
    {"name": "Together AI (Free)", "category": "AI", "description": "API access to open-source LLMs including Llama and Mistral.", "api_url": "https://docs.together.ai/reference/inference", "pricing": "Free – $25 credit on sign-up", "affiliate_link": "https://together.ai", "docs_url": "https://docs.together.ai"},
    {"name": "Mistral AI (Free)", "category": "AI", "description": "Open-weight large language models with API access.", "api_url": "https://docs.mistral.ai/api/", "pricing": "Free trial credit", "affiliate_link": "https://mistral.ai", "docs_url": "https://docs.mistral.ai"},
    {"name": "Groq (Free)", "category": "AI", "description": "Ultra-fast LLM inference platform.", "api_url": "https://console.groq.com/docs/api-reference", "pricing": "Free tier available", "affiliate_link": "https://groq.com", "docs_url": "https://console.groq.com/docs"},
    {"name": "Perplexity AI (Free)", "category": "AI", "description": "AI-powered search engine and question answering.", "api_url": "https://docs.perplexity.ai/reference/post_chat_completions", "pricing": "Free – 5 requests/min", "affiliate_link": "https://perplexity.ai", "docs_url": "https://docs.perplexity.ai"},
    {"name": "AssemblyAI (Free)", "category": "AI", "description": "Speech-to-text API with AI features like sentiment analysis.", "api_url": "https://www.assemblyai.com/docs/api-reference/", "pricing": "Free – 100 hours", "affiliate_link": "https://assemblyai.com", "docs_url": "https://www.assemblyai.com/docs"},
    {"name": "Deepgram (Free)", "category": "AI", "description": "AI speech recognition API for developers.", "api_url": "https://developers.deepgram.com/reference/listen-file", "pricing": "Free – $200 credit", "affiliate_link": "https://deepgram.com", "docs_url": "https://developers.deepgram.com"},
    {"name": "ElevenLabs (Free)", "category": "AI", "description": "AI voice synthesis and cloning platform.", "api_url": "https://elevenlabs.io/docs/api-reference/text-to-speech", "pricing": "Free – 10k chars/month", "affiliate_link": "https://elevenlabs.io", "docs_url": "https://elevenlabs.io/docs"},
    {"name": "Speechify (Free)", "category": "AI", "description": "Text-to-speech platform for content and accessibility.", "api_url": "https://docs.speechify.com/api-reference", "pricing": "Free 14-day trial", "affiliate_link": "https://speechify.com", "docs_url": "https://docs.speechify.com"},
    {"name": "Pinecone (Free)", "category": "AI", "description": "Vector database for AI applications and semantic search.", "api_url": "https://docs.pinecone.io/reference/api/introduction", "pricing": "Free – 2M vectors", "affiliate_link": "https://pinecone.io", "docs_url": "https://docs.pinecone.io"},
    {"name": "Weaviate (Free)", "category": "AI", "description": "Open-source vector database for AI-native applications.", "api_url": "https://weaviate.io/developers/weaviate/api/rest", "pricing": "Free self-hosted / cloud sandbox", "affiliate_link": "https://weaviate.io", "docs_url": "https://weaviate.io/developers/weaviate"},
    {"name": "Chroma (Free)", "category": "AI", "description": "Open-source embedding database for LLM applications.", "api_url": "https://docs.trychroma.com/reference/py-client", "pricing": "Free open-source", "affiliate_link": "https://trychroma.com", "docs_url": "https://docs.trychroma.com"},
    {"name": "LangChain (Free)", "category": "AI", "description": "Framework for building LLM-powered applications.", "api_url": "https://python.langchain.com/api_reference/", "pricing": "Free open-source", "affiliate_link": "https://python.langchain.com", "docs_url": "https://python.langchain.com/docs"},
    {"name": "LlamaIndex (Free)", "category": "AI", "description": "Data framework for LLM-based applications.", "api_url": "https://docs.llamaindex.ai/en/stable/api_reference/", "pricing": "Free open-source", "affiliate_link": "https://llamaindex.ai", "docs_url": "https://docs.llamaindex.ai"},
    {"name": "Weights & Biases (Free)", "category": "AI", "description": "ML experiment tracking, dataset versioning, and model management.", "api_url": "https://docs.wandb.ai/ref/python/", "pricing": "Free – unlimited projects", "affiliate_link": "https://wandb.ai", "docs_url": "https://docs.wandb.ai"},
    {"name": "Roboflow (Free)", "category": "AI", "description": "Computer vision platform for training and deploying models.", "api_url": "https://docs.roboflow.com/api-reference", "pricing": "Free – 3 source projects", "affiliate_link": "https://roboflow.com", "docs_url": "https://docs.roboflow.com"},
    {"name": "Scale AI (Free)", "category": "AI", "description": "AI data platform for training dataset generation.", "api_url": "https://docs.scale.com/reference/quick-start", "pricing": "Free sandbox", "affiliate_link": "https://scale.com", "docs_url": "https://docs.scale.com"},
    {"name": "Clarifai (Free)", "category": "AI", "description": "AI platform for computer vision and NLP.", "api_url": "https://docs.clarifai.com/api-guide/api-overview/", "pricing": "Free – 1000 ops/month", "affiliate_link": "https://clarifai.com", "docs_url": "https://docs.clarifai.com"},
    {"name": "Runway ML (Free)", "category": "AI", "description": "AI-powered creative tools for video editing and generation.", "api_url": "https://docs.runwayml.com/", "pricing": "Free – 125 credits", "affiliate_link": "https://runwayml.com", "docs_url": "https://docs.runwayml.com"},
    {"name": "Midjourney (Free)", "category": "AI", "description": "AI image generation platform via Discord.", "api_url": "https://docs.midjourney.com/docs/quick-start", "pricing": "Free – 25 queries", "affiliate_link": "https://midjourney.com", "docs_url": "https://docs.midjourney.com"},
    {"name": "DALL-E (OpenAI Free)", "category": "AI", "description": "Text-to-image generation model by OpenAI.", "api_url": "https://platform.openai.com/docs/api-reference/images", "pricing": "Free credit on sign-up", "affiliate_link": "https://openai.com/dall-e", "docs_url": "https://platform.openai.com/docs/guides/images"},
    {"name": "Eden AI (Free)", "category": "AI", "description": "Unified API aggregating AI services from multiple providers.", "api_url": "https://docs.edenai.run/reference/start-your-ai-journey-with-edenai", "pricing": "Free – $1 credit on sign-up", "affiliate_link": "https://edenai.run", "docs_url": "https://docs.edenai.run"},
    {"name": "Banana (Free)", "category": "AI", "description": "Serverless GPU platform for deploying ML models.", "api_url": "https://docs.banana.dev/banana-docs/core-concepts/get-started", "pricing": "Free – $5 credit on sign-up", "affiliate_link": "https://banana.dev", "docs_url": "https://docs.banana.dev"},
    {"name": "Modal (Free)", "category": "AI", "description": "Serverless cloud infrastructure for AI and ML workloads.", "api_url": "https://modal.com/docs/reference/", "pricing": "Free – $30 credit/month", "affiliate_link": "https://modal.com", "docs_url": "https://modal.com/docs"},
]


def get_connection():
    """Return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialise the database schema and seed data."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            api_url TEXT,
            pricing TEXT,
            affiliate_link TEXT,
            docs_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            plan TEXT NOT NULL DEFAULT 'free',
            stripe_customer_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS affiliate_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_id INTEGER NOT NULL,
            session_id TEXT,
            converted INTEGER DEFAULT 0,
            commission REAL DEFAULT 0.0,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tool_id) REFERENCES tools(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS revenue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT DEFAULT '',
            service TEXT DEFAULT '',
            message TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS demo_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demo_name TEXT NOT NULL,
            user_input TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed tools only if empty
    c.execute("SELECT COUNT(*) FROM tools")
    if c.fetchone()[0] == 0:
        c.executemany("""
            INSERT OR IGNORE INTO tools
              (name, category, description, api_url, pricing, affiliate_link, docs_url)
            VALUES (:name, :category, :description, :api_url, :pricing, :affiliate_link, :docs_url)
        """, SAAS_TOOLS)

    conn.commit()
    conn.close()


def get_all_tools():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tools ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tools_by_category(category: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tools WHERE LOWER(category)=LOWER(?) ORDER BY name",
        (category,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_tools(query: str):
    like = f"%{query}%"
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM tools
           WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
           ORDER BY name""",
        (like, like, like)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tool_by_id(tool_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tools WHERE id=?", (tool_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_categories():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) as count FROM tools GROUP BY category ORDER BY category"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_tool(tool: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO tools (name, category, description, api_url, pricing, affiliate_link, docs_url)
        VALUES (:name, :category, :description, :api_url, :pricing, :affiliate_link, :docs_url)
    """, tool)
    conn.commit()
    conn.close()


def record_affiliate_click(tool_id: int, session_id: str = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO affiliate_clicks (tool_id, session_id) VALUES (?, ?)",
        (tool_id, session_id)
    )
    conn.commit()
    conn.close()


def record_conversion(tool_id: int, commission: float):
    conn = get_connection()
    conn.execute(
        "UPDATE affiliate_clicks SET converted=1, commission=? WHERE tool_id=? AND converted=0",
        (commission, tool_id)
    )
    conn.execute(
        "INSERT INTO revenue (source, amount) VALUES (?, ?)",
        (f"affiliate_tool_{tool_id}", commission)
    )
    conn.commit()
    conn.close()


def get_revenue_summary():
    conn = get_connection()
    total = conn.execute("SELECT COALESCE(SUM(amount),0) FROM revenue").fetchone()[0]
    clicks = conn.execute("SELECT COUNT(*) FROM affiliate_clicks").fetchone()[0]
    conversions = conn.execute(
        "SELECT COUNT(*) FROM affiliate_clicks WHERE converted=1"
    ).fetchone()[0]
    conn.close()
    return {"total_revenue": total, "total_clicks": clicks, "conversions": conversions}


def add_subscription(email: str, plan: str = "free", stripe_customer_id: str = None):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO subscriptions (email, plan, stripe_customer_id) VALUES (?, ?, ?)",
        (email, plan, stripe_customer_id)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    tools = get_all_tools()
    print(f"Database initialised with {len(tools)} tools.")
    cats = get_categories()
    for cat in cats:
        print(f"  {cat['category']}: {cat['count']} tools")

# ---------------------------------------------------------------------------
# Extended database functions for test compatibility
# ---------------------------------------------------------------------------

def save_lead(name: str, email: str, company: str = "", service: str = "", message: str = "") -> int:
    """Save a lead to the database. Returns the new row ID."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO leads (name, email, company, service, message) VALUES (?, ?, ?, ?, ?)",
                    (name, email, company, service, message))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def record_demo(demo_name: str, user_input: str = "") -> None:
    """Record a demo interaction."""
    conn = get_connection()
    try:
        conn.execute("INSERT INTO demo_events (demo_name, user_input) VALUES (?, ?)", (demo_name, user_input))
        conn.commit()
    finally:
        conn.close()


def record_chat(user_message: str, bot_response: str = "") -> None:
    """Record a chat interaction."""
    conn = get_connection()
    try:
        conn.execute("INSERT INTO chat_events (user_message, bot_response) VALUES (?, ?)", (user_message, bot_response))
        conn.commit()
    finally:
        conn.close()


def get_analytics() -> dict:
    """Return analytics data."""
    conn = get_connection()
    try:
        # Total leads
        try:
            total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        except Exception:
            total_leads = 0
        # Demo runs by type
        try:
            rows = conn.execute("SELECT demo_name, COUNT(*) as cnt FROM demo_events GROUP BY demo_name").fetchall()
            demo_runs = {row["demo_name"]: row["cnt"] for row in rows}
        except Exception:
            demo_runs = {}
        # Chat interactions
        try:
            chat_interactions = conn.execute("SELECT COUNT(*) FROM chat_events").fetchone()[0]
        except Exception:
            chat_interactions = 0
        return {
            "total_leads": total_leads,
            "demo_runs": demo_runs,
            "chat_interactions": chat_interactions,
        }
    finally:
        conn.close()
