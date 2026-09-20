-- Newsletter Backlog Table
CREATE TABLE GrowthAgent_newsletter_backlog (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product         TEXT NOT NULL,
  section_type    TEXT NOT NULL,
  -- Synthetix AI: 'sports_science' | 'world_cup' | 'research' | 'product' | 'founder'
  -- CloudPulse: 'healthcare_research' | 'rehabilitation' | 'rpm' | 'product' | 'founder'
  -- Studio: 'ai_healthtech' | 'startup_ecosystem' | 'engineering' | 'founder' | 'case_study'
  headline        TEXT NOT NULL,
  body            TEXT NOT NULL,
  source_signal_id UUID,
  relevance_score INT DEFAULT 50,
  used            BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Experiments Table
CREATE TABLE GrowthAgent_experiments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product         TEXT NOT NULL,
  hypothesis      TEXT NOT NULL,
  -- e.g. "Contrarian hooks outperform educational hooks for Synthetix AI on LinkedIn"
  variable        TEXT NOT NULL,
  -- e.g. "hook_type"
  control_value   TEXT NOT NULL,
  -- e.g. "educational"
  test_value      TEXT NOT NULL,
  -- e.g. "contrarian"
  duration_days   INT DEFAULT 14,
  primary_kpi     TEXT NOT NULL,
  -- e.g. "engagement_rate"
  status          TEXT DEFAULT 'proposed',
  -- 'proposed' | 'running' | 'completed' | 'inconclusive'
  control_result  NUMERIC(10,2),
  test_result     NUMERIC(10,2),
  winner          TEXT,
  -- 'control' | 'test' | 'inconclusive'
  learning        TEXT,
  -- "Contrarian hooks produced 1.8x engagement for Synthetix AI sports content"
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at    TIMESTAMPTZ
);
