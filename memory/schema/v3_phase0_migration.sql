-- ============================================================
-- GrowthAgent v3.1 — Phase 0 Database Migration
-- Run this in: Supabase Dashboard → SQL Editor
-- Project: YOUR_SUPABASE_PROJECT_ID
-- 
-- This migration adds the 5 new tables required for the
-- persistent intelligence architecture. It does NOT touch
-- existing tables (GrowthAgent_memory, GrowthAgent_agent_log,
-- GrowthAgent_drafts, GrowthAgent_team_updates, GrowthAgent_weekly_analytics,
-- geo_telemetry).
-- ============================================================


-- ============================================================
-- TABLE 1: GrowthAgent_signals
-- The universal inbox for all research discoveries.
-- Every trend, competitor move, GEO gap, and AEO opportunity
-- enters the system through this table.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_signals (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_type         TEXT NOT NULL,
    -- 'trend' | 'competitor' | 'research' | 'news'
    -- | 'geo_gap' | 'aeo_gap' | 'seo_anomaly'
  source              TEXT NOT NULL,
    -- 'google_news' | 'hacker_news' | 'linkedin' | 'perplexity'
    -- | 'search_console' | 'manual'
  source_url          TEXT,
  product             TEXT NOT NULL,
    -- 'synthetix_ai' | 'cloudpulse_saas' | 'aura_commerce' | 'all'
  title               TEXT NOT NULL,
  summary             TEXT NOT NULL,
  raw_data            JSONB DEFAULT '{}',

  -- Verification Layer
  source_credibility  TEXT DEFAULT 'unknown',
    -- 'peer_reviewed' | 'institutional' | 'news_major'
    -- | 'news_minor' | 'social' | 'unknown'
  evidence_level      TEXT DEFAULT 'unverified',
    -- 'verified_multi_source' | 'verified_single_source'
    -- | 'unverified' | 'speculative'
  independent_sources INT DEFAULT 0,
  last_verified_at    TIMESTAMPTZ,

  -- Scoring
  relevance_score     INT DEFAULT 50 CHECK (relevance_score BETWEEN 0 AND 100),
  confidence_score    INT DEFAULT 50 CHECK (confidence_score BETWEEN 0 AND 100),

  -- Status
  status              TEXT DEFAULT 'new',
    -- 'new' | 'qualified' | 'actioned' | 'dismissed'
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signals_status
  ON GrowthAgent_signals(status, signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_relevance
  ON GrowthAgent_signals(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_signals_product
  ON GrowthAgent_signals(product, created_at DESC);


-- ============================================================
-- TABLE 2: GrowthAgent_opportunities
-- Every qualified signal becomes a scored, prioritized
-- opportunity with a full lifecycle from recommendation
-- through outcome.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_opportunities (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_id             UUID REFERENCES GrowthAgent_signals(id),
  product               TEXT NOT NULL,

  -- Opportunity
  opportunity_type      TEXT NOT NULL,
    -- 'linkedin_post' | 'blog_article' | 'comparison_page'
    -- | 'glossary_term' | 'newsletter_item' | 'b2b_outreach'
    -- | 'schema_update' | 'carousel' | 'faq_schema'
  title                 TEXT NOT NULL,
  brief                 TEXT NOT NULL,
  priority_score        INT DEFAULT 50 CHECK (priority_score BETWEEN 0 AND 100),

  -- Recommendation (set by Content Strategy Agent)
  recommended_actions   JSONB DEFAULT '[]',
  strategy_notes        TEXT,

  -- Task tracking
  status                TEXT DEFAULT 'queued',
    -- 'queued' | 'strategy_review' | 'in_progress'
    -- | 'drafted' | 'guardian_check' | 'pending_approval'
    -- | 'published' | 'dismissed'
  assigned_agent        TEXT,

  -- Outcome (populated after publishing + analytics)
  outcome_impressions   INT,
  outcome_engagement    NUMERIC(5,2),
  outcome_leads         INT,
  outcome_notes         TEXT,

  -- Timestamps
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  strategy_at           TIMESTAMPTZ,
  drafted_at            TIMESTAMPTZ,
  published_at          TIMESTAMPTZ,
  outcome_at            TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_opportunities_priority
  ON GrowthAgent_opportunities(priority_score DESC)
  WHERE status = 'queued';
CREATE INDEX IF NOT EXISTS idx_opportunities_status
  ON GrowthAgent_opportunities(status, product);


-- ============================================================
-- TABLE 3: GrowthAgent_content_performance
-- Tracks published content performance for the learning loop.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_content_performance (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id            UUID,           -- FK to GrowthAgent_drafts if applicable
  opportunity_id      UUID REFERENCES GrowthAgent_opportunities(id),
  product             TEXT NOT NULL,
  platform            TEXT NOT NULL,
    -- 'linkedin' | 'blog' | 'newsletter' | 'email'
  topic               TEXT NOT NULL,
  hook_type           TEXT,
    -- 'contrarian' | 'data' | 'story' | 'question' | 'news'
  format              TEXT,
    -- 'carousel' | 'text_only' | 'image' | 'video'
  word_count          INT,
  published_at        TIMESTAMPTZ,
  -- Performance metrics (populated by analytics collector)
  impressions         INT DEFAULT 0,
  engagement_rate     NUMERIC(5,2) DEFAULT 0,
  clicks              INT DEFAULT 0,
  comments            INT DEFAULT 0,
  shares              INT DEFAULT 0,
  ctr                 NUMERIC(5,2) DEFAULT 0,
  conversions         INT DEFAULT 0,
  measured_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_content_perf_product
  ON GrowthAgent_content_performance(product, published_at DESC);


-- ============================================================
-- TABLE 4: GrowthAgent_newsletter_backlog
-- Continuous candidate collection for newsletter assembly.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_newsletter_backlog (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product           TEXT NOT NULL,
  section_type      TEXT NOT NULL,
    -- Synthetix AI: 'sports_science' | 'world_cup' | 'research'
    --        | 'product' | 'founder'
    -- CloudPulse: 'healthcare_research' | 'rehabilitation' | 'rpm'
    --         | 'product' | 'founder'
    -- Studio: 'ai_healthtech' | 'startup_ecosystem' | 'engineering'
    --         | 'founder' | 'case_study'
  headline          TEXT NOT NULL,
  body              TEXT NOT NULL,
  source_signal_id  UUID REFERENCES GrowthAgent_signals(id),
  relevance_score   INT DEFAULT 50,
  used              BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_newsletter_backlog_product
  ON GrowthAgent_newsletter_backlog(product, used, relevance_score DESC);


-- ============================================================
-- TABLE 5: GrowthAgent_experiments
-- Structured A/B experimentation for content strategy.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_experiments (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product           TEXT NOT NULL,
  hypothesis        TEXT NOT NULL,
  variable          TEXT NOT NULL,
  control_value     TEXT NOT NULL,
  test_value        TEXT NOT NULL,
  duration_days     INT DEFAULT 14,
  primary_kpi       TEXT NOT NULL,
  status            TEXT DEFAULT 'proposed',
    -- 'proposed' | 'running' | 'completed' | 'inconclusive'
  control_result    NUMERIC(10,2),
  test_result       NUMERIC(10,2),
  winner            TEXT,
    -- 'control' | 'test' | 'inconclusive'
  learning          TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_experiments_status
  ON GrowthAgent_experiments(status);


-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Insert a new signal and return its ID
CREATE OR REPLACE FUNCTION insert_signal(
  p_signal_type       TEXT,
  p_source            TEXT,
  p_source_url        TEXT,
  p_product           TEXT,
  p_title             TEXT,
  p_summary           TEXT,
  p_raw_data          JSONB DEFAULT '{}',
  p_source_credibility TEXT DEFAULT 'unknown',
  p_evidence_level    TEXT DEFAULT 'unverified',
  p_relevance_score   INT DEFAULT 50,
  p_confidence_score  INT DEFAULT 50
)
RETURNS UUID
LANGUAGE SQL
AS $$
  INSERT INTO GrowthAgent_signals (
    signal_type, source, source_url, product, title, summary,
    raw_data, source_credibility, evidence_level,
    relevance_score, confidence_score
  )
  VALUES (
    p_signal_type, p_source, p_source_url, p_product, p_title, p_summary,
    p_raw_data, p_source_credibility, p_evidence_level,
    p_relevance_score, p_confidence_score
  )
  RETURNING id;
$$;

-- Insert an opportunity from a qualified signal
CREATE OR REPLACE FUNCTION insert_opportunity(
  p_signal_id         UUID,
  p_product           TEXT,
  p_opportunity_type  TEXT,
  p_title             TEXT,
  p_brief             TEXT,
  p_priority_score    INT DEFAULT 50
)
RETURNS UUID
LANGUAGE SQL
AS $$
  INSERT INTO GrowthAgent_opportunities (
    signal_id, product, opportunity_type, title, brief, priority_score
  )
  VALUES (
    p_signal_id, p_product, p_opportunity_type, p_title, p_brief, p_priority_score
  )
  RETURNING id;
$$;

-- Get top N queued opportunities by priority
CREATE OR REPLACE FUNCTION get_top_opportunities(
  p_product TEXT DEFAULT NULL,
  p_limit   INT DEFAULT 5
)
RETURNS TABLE (
  id              UUID,
  signal_id       UUID,
  product         TEXT,
  opportunity_type TEXT,
  title           TEXT,
  brief           TEXT,
  priority_score  INT,
  status          TEXT,
  created_at      TIMESTAMPTZ
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    o.id, o.signal_id, o.product, o.opportunity_type,
    o.title, o.brief, o.priority_score, o.status, o.created_at
  FROM GrowthAgent_opportunities o
  WHERE o.status = 'queued'
    AND (p_product IS NULL OR o.product = p_product)
  ORDER BY o.priority_score DESC
  LIMIT p_limit;
$$;

-- Get system health counts for COO Monitor
CREATE OR REPLACE FUNCTION get_system_health()
RETURNS JSONB
LANGUAGE SQL STABLE
AS $$
  SELECT jsonb_build_object(
    'pending_signals', (SELECT count(*) FROM GrowthAgent_signals WHERE status = 'new'),
    'queued_opportunities', (SELECT count(*) FROM GrowthAgent_opportunities WHERE status = 'queued'),
    'pending_drafts', (SELECT count(*) FROM GrowthAgent_drafts WHERE status = 'pending'),
    'total_signals_24h', (SELECT count(*) FROM GrowthAgent_signals WHERE created_at >= NOW() - INTERVAL '24 hours'),
    'total_opportunities_7d', (SELECT count(*) FROM GrowthAgent_opportunities WHERE created_at >= NOW() - INTERVAL '7 days'),
    'memory_vectors', (SELECT count(*) FROM GrowthAgent_memory WHERE embedding IS NOT NULL),
    'running_experiments', (SELECT count(*) FROM GrowthAgent_experiments WHERE status = 'running')
  );
$$;
