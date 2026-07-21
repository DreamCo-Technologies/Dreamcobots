-- DreamCo Money Operating System — PostgreSQL/SQLite Compatible Schema
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- Note: JSONB is PostgreSQL-specific; use TEXT for SQLite deployments.

-- ──────────────────────────────────────────────────────────────────────────────
-- users
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    tier            VARCHAR(20) NOT NULL DEFAULT 'FREE'
                        CHECK (tier IN ('FREE', 'PRO', 'ENTERPRISE')),
    stripe_customer_id VARCHAR(100),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_tier ON users (tier);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at);

-- ──────────────────────────────────────────────────────────────────────────────
-- leads
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leads (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users (id) ON DELETE SET NULL,
    name        VARCHAR(255) NOT NULL DEFAULT 'Unknown',
    email       VARCHAR(255) NOT NULL,
    phone       VARCHAR(50),
    source      VARCHAR(100) NOT NULL DEFAULT 'organic',
    category    VARCHAR(100) NOT NULL DEFAULT 'general',
    score       INTEGER NOT NULL DEFAULT 0
                    CHECK (score >= 0 AND score <= 100),
    status      VARCHAR(20) NOT NULL DEFAULT 'new'
                    CHECK (status IN ('new', 'contacted', 'qualified', 'sold', 'rejected')),
    sold_at     TIMESTAMP,
    sold_price  NUMERIC(12, 2) CHECK (sold_price >= 0),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads (user_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads (email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads (status);
CREATE INDEX IF NOT EXISTS idx_leads_category ON leads (category);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads (score);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads (created_at);

-- ──────────────────────────────────────────────────────────────────────────────
-- deals
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS deals (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users (id) ON DELETE SET NULL,
    bot_name    VARCHAR(100) NOT NULL,
    deal_type   VARCHAR(100) NOT NULL,
    value       NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (value >= 0),
    status      VARCHAR(30) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'negotiating', 'closed_won', 'closed_lost', 'pending')),
    metadata    JSONB,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    closed_at   TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_deals_user_id ON deals (user_id);
CREATE INDEX IF NOT EXISTS idx_deals_bot_name ON deals (bot_name);
CREATE INDEX IF NOT EXISTS idx_deals_status ON deals (status);
CREATE INDEX IF NOT EXISTS idx_deals_deal_type ON deals (deal_type);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON deals (created_at);
CREATE INDEX IF NOT EXISTS idx_deals_closed_at ON deals (closed_at);

-- ──────────────────────────────────────────────────────────────────────────────
-- automation_logs
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS automation_logs (
    id                  SERIAL PRIMARY KEY,
    bot_name            VARCHAR(100) NOT NULL,
    action              VARCHAR(255) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'success'
                            CHECK (status IN ('success', 'failure', 'skipped', 'running')),
    result              JSONB,
    revenue_generated   NUMERIC(14, 2) NOT NULL DEFAULT 0,
    duration_ms         INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_automation_logs_bot_name ON automation_logs (bot_name);
CREATE INDEX IF NOT EXISTS idx_automation_logs_status ON automation_logs (status);
CREATE INDEX IF NOT EXISTS idx_automation_logs_created_at ON automation_logs (created_at);

-- ──────────────────────────────────────────────────────────────────────────────
-- revenue
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS revenue (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(100) NOT NULL,
    amount          NUMERIC(14, 2) NOT NULL CHECK (amount >= 0),
    currency        VARCHAR(10) NOT NULL DEFAULT 'USD',
    payment_method  VARCHAR(50) NOT NULL DEFAULT 'stripe'
                        CHECK (payment_method IN ('stripe', 'paypal', 'crypto', 'wire', 'check', 'other')),
    metadata        JSONB,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_revenue_source ON revenue (source);
CREATE INDEX IF NOT EXISTS idx_revenue_payment_method ON revenue (payment_method);
CREATE INDEX IF NOT EXISTS idx_revenue_created_at ON revenue (created_at);

-- ──────────────────────────────────────────────────────────────────────────────
-- bot_schedules
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bot_schedules (
    id              SERIAL PRIMARY KEY,
    bot_name        VARCHAR(100) NOT NULL UNIQUE,
    schedule_cron   VARCHAR(100) NOT NULL,
    last_run        TIMESTAMP,
    next_run        TIMESTAMP,
    enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bot_schedules_bot_name ON bot_schedules (bot_name);
CREATE INDEX IF NOT EXISTS idx_bot_schedules_enabled ON bot_schedules (enabled);
CREATE INDEX IF NOT EXISTS idx_bot_schedules_next_run ON bot_schedules (next_run);
