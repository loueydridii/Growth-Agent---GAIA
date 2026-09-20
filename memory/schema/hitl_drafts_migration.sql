-- ============================================================
-- GrowthAgent — Phase 3: Layer 6 HITL Drafts Migration
-- Table: GrowthAgent_drafts
-- Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS GrowthAgent_drafts (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_name       TEXT NOT NULL,          -- e.g. 'LinkedIn Content Agent', 'Newsletter Agent', 'B2B Outreach Agent'
  brand_tag        TEXT NOT NULL,          -- 'CloudPulse' | 'Synthetix AI' | 'all'
  category         TEXT NOT NULL,          -- 'linkedin_post' | 'newsletter' | 'b2b_email' | 'seo_blog'
  draft_content    TEXT NOT NULL,          -- Full markdown/HTML of the draft
  target_channel   TEXT,                   -- e.g. 'LinkedIn Page', 'Brevo Campaign', 'Gmail Outbox'
  status           TEXT DEFAULT 'pending', -- 'pending' | 'approved' | 'rejected' | 'revised' | 'published'
  created_by_bot   TEXT DEFAULT 'GrowthAgent',
  reviewed_by      TEXT,                   -- Discord username who clicked Approve/Reject
  original_msg_id  TEXT,                   -- Discord message ID for interaction tracking
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  reviewed_at      TIMESTAMPTZ,
  published_at     TIMESTAMPTZ
);

-- Index for fast lookup of pending drafts by status and category
CREATE INDEX IF NOT EXISTS idx_GrowthAgent_drafts_status_category
  ON GrowthAgent_drafts (status, category);

-- Index for looking up draft by Discord message ID
CREATE INDEX IF NOT EXISTS idx_GrowthAgent_drafts_msg_id
  ON GrowthAgent_drafts (original_msg_id);

-- ============================================================
-- FUNCTION: log_hitl_draft(agent, brand, cat, content, channel, msg_id)
-- Call this from any drafting workflow to store a draft for HITL review
-- ============================================================
CREATE OR REPLACE FUNCTION log_hitl_draft(
  p_agent_name       TEXT,
  p_brand_tag        TEXT,
  p_category         TEXT,
  p_draft_content    TEXT,
  p_target_channel   TEXT DEFAULT NULL,
  p_original_msg_id  TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE SQL
AS $$
  INSERT INTO GrowthAgent_drafts (
    agent_name, brand_tag, category, draft_content, target_channel, original_msg_id, status
  )
  VALUES (
    p_agent_name, p_brand_tag, p_category, p_draft_content, p_target_channel, p_original_msg_id, 'pending'
  )
  RETURNING id;
$$;

-- ============================================================
-- FUNCTION: review_hitl_draft(draft_id, review_action, reviewer)
-- Updates draft status when Discord button is clicked
-- ============================================================
CREATE OR REPLACE FUNCTION review_hitl_draft(
  p_draft_id   UUID,
  p_action     TEXT, -- 'approve' | 'reject' | 'revise'
  p_reviewer   TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE GrowthAgent_drafts
  SET
    status      = CASE 
                    WHEN p_action = 'approve' THEN 'approved'
                    WHEN p_action = 'reject'  THEN 'rejected'
                    WHEN p_action = 'revise'  THEN 'revised'
                    ELSE status
                  END,
    reviewed_by = p_reviewer,
    reviewed_at = NOW()
  WHERE id = p_draft_id;
  
  RETURN FOUND;
END;
$$;
