-- ============================================================
-- GrowthAgent — Live GEO Telemetry Schema
-- Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

-- Create the geo_telemetry table for continuous prompt tracking
CREATE TABLE IF NOT EXISTS geo_telemetry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_text TEXT NOT NULL,
  product TEXT NOT NULL,
  llm_engine TEXT NOT NULL,
  brand_mentioned BOOLEAN NOT NULL,
  rank INT,
  competitors_mentioned TEXT[],
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- FUNCTION: get_weekly_geo_score(filter_product)
-- Returns the percentage of successful brand citations over the 
-- last 7 days. Can be filtered by product or return an aggregate.
-- ============================================================
CREATE OR REPLACE FUNCTION get_weekly_geo_score(p_product TEXT DEFAULT 'all')
RETURNS FLOAT
LANGUAGE SQL STABLE
AS $$
  SELECT 
    CASE 
      WHEN count(*) = 0 THEN 0.0
      ELSE ROUND(((count(CASE WHEN brand_mentioned THEN 1 END)::FLOAT / count(*)::FLOAT) * 100.0)::numeric, 2)::FLOAT
    END
  FROM geo_telemetry
  WHERE created_at >= NOW() - INTERVAL '7 days'
    AND (p_product = 'all' OR product = p_product);
$$;
