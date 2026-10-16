-- ============================================================
-- GrowthAgent — Phase 1: Memory Foundation
-- Supabase + pgvector Schema
-- Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

-- Step 1: Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing table to allow changing vector dimensions
DROP TABLE IF EXISTS GrowthAgent_memory CASCADE;

-- ============================================================
-- TABLE: GrowthAgent_memory
-- The single source of truth for all GrowthAgent agent context.
-- Dimension 768 matches Gemini text-embedding-004.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_memory (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product       TEXT NOT NULL,      -- 'cloudpulse_saas' | 'synthetix_ai' | 'aura_commerce' | 'all'
  category      TEXT NOT NULL,      -- 'brand_voice' | 'icp' | 'product_guide' | 'competitor_intel'
                                    -- | 'blog_article' | 'linkedin_post' | 'newsletter'
                                    -- | 'outreach_email' | 'team_update'
  subcategory   TEXT,               -- e.g. 'tone_anchor', 'devops_dave', 'pricing_tiers'
  content       TEXT NOT NULL,      -- Human-readable text agents will read
  metadata      JSONB DEFAULT '{}', -- Structured extras (source stats, codes, etc.)
  embedding     vector(3072),        -- Gemini text-embedding-004 vector
  source_file   TEXT,               -- Origin file for traceability
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLE: GrowthAgent_team_updates
-- Stores weekly product/business updates from leadership & team
-- Injected into Memory before each agent run.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_team_updates (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_name   TEXT NOT NULL,      -- e.g. 'TeamLead', 'ProductLead', 'intern'
  product       TEXT,               -- Which product the update is about
  update_text   TEXT NOT NULL,      -- The actual update content
  ingested      BOOLEAN DEFAULT FALSE, -- Whether it's been embedded into GrowthAgent_memory
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLE: GrowthAgent_agent_log
-- Logs every agent task, its inputs, outputs, and status.
-- Used by the Project Manager (AI COO) and Operations Dashboard.
-- ============================================================
CREATE TABLE IF NOT EXISTS GrowthAgent_agent_log (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_name    TEXT NOT NULL,      -- 'b2b_outreach' | 'linkedin' | 'blog' | 'orchestrator' etc.
  task_input    TEXT,               -- What the agent was given
  task_output   TEXT,               -- What the agent produced
  status        TEXT DEFAULT 'pending', -- 'pending' | 'approved' | 'rejected' | 'published' | 'failed'
  product       TEXT,
  approved_by   TEXT,               -- 'intern' | 'teamlead' | 'auto'
  execution_ms  INT,                -- How long the task took
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Vector similarity index (cosine distance — best for text embeddings)
CREATE INDEX IF NOT EXISTS idx_GrowthAgent_memory_embedding
  ON GrowthAgent_memory USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Fast filtering by product and category
CREATE INDEX IF NOT EXISTS idx_GrowthAgent_memory_product_category
  ON GrowthAgent_memory (product, category);

-- Agent log lookup
CREATE INDEX IF NOT EXISTS idx_GrowthAgent_agent_log_agent_status
  ON GrowthAgent_agent_log (agent_name, status);

-- ============================================================
-- FUNCTION: search_memory(query_embedding, match_count, filter_product)
-- Agents call this to retrieve relevant context before generating.
-- ============================================================
CREATE OR REPLACE FUNCTION search_memory(
  query_embedding vector(3072),
  match_count     INT DEFAULT 5,
  filter_product  TEXT DEFAULT NULL
)
RETURNS TABLE (
  id          UUID,
  product     TEXT,
  category    TEXT,
  subcategory TEXT,
  content     TEXT,
  metadata    JSONB,
  similarity  FLOAT
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    m.id,
    m.product,
    m.category,
    m.subcategory,
    m.content,
    m.metadata,
    1 - (m.embedding <=> query_embedding) AS similarity
  FROM GrowthAgent_memory m
  WHERE
    (filter_product IS NULL OR m.product = filter_product OR m.product = 'all')
    AND m.embedding IS NOT NULL
  ORDER BY m.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- ============================================================
-- FUNCTION: log_agent_task(agent, input, output, status, product)
-- Call this at the end of every n8n agent workflow to log the run.
-- ============================================================
CREATE OR REPLACE FUNCTION log_agent_task(
  p_agent_name  TEXT,
  p_task_input  TEXT,
  p_task_output TEXT,
  p_status      TEXT DEFAULT 'pending',
  p_product     TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE SQL
AS $$
  INSERT INTO GrowthAgent_agent_log (agent_name, task_input, task_output, status, product)
  VALUES (p_agent_name, p_task_input, p_task_output, p_status, p_product)
  RETURNING id;
$$;
