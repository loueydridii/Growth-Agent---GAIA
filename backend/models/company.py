"""
backend/models/company.py — SQLAlchemy models for company config, brand, and ICP.
All data written here is the single source of truth for agent personalization.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, JSON, DateTime, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base


def _now():
    return datetime.now(timezone.utc)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    website: Mapped[str] = mapped_column(String(512), nullable=True)
    industry: Mapped[str] = mapped_column(String(128), nullable=True)
    stage: Mapped[str] = mapped_column(String(64), nullable=True)  # startup/scaleup/enterprise
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class BrandVoice(Base):
    __tablename__ = "brand_voice"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, nullable=False)
    tone: Mapped[str] = mapped_column(String(64), nullable=True)       # professional/casual/bold/technical
    rules: Mapped[list] = mapped_column(JSON, default=list)            # list of writing rules
    forbidden_phrases: Mapped[list] = mapped_column(JSON, default=list)
    hex_primary: Mapped[str] = mapped_column(String(16), nullable=True)
    hex_secondary: Mapped[str] = mapped_column(String(16), nullable=True)
    context_md: Mapped[str] = mapped_column(Text, nullable=True)       # full context.md content
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ICP(Base):
    """Ideal Customer Profile — multiple per company."""
    __tablename__ = "icps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)      # e.g. "VP Eng at 200-person SaaS"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    seniority: Mapped[str] = mapped_column(String(128), nullable=True)
    company_size_min: Mapped[int] = mapped_column(nullable=True)
    company_size_max: Mapped[int] = mapped_column(nullable=True)
    industries: Mapped[list] = mapped_column(JSON, default=list)
    pain_points: Mapped[list] = mapped_column(JSON, default=list)
    goals: Mapped[list] = mapped_column(JSON, default=list)
    objections: Mapped[list] = mapped_column(JSON, default=list)
    channels: Mapped[list] = mapped_column(JSON, default=list)          # ["linkedin", "email"]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CEOGoal(Base):
    """The active north-star metric the agent is driving toward."""
    __tablename__ = "ceo_goals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, nullable=False)
    metric: Mapped[str] = mapped_column(String(128), nullable=False)   # pipeline, leads, revenue
    target: Mapped[str] = mapped_column(String(64), nullable=False)    # +30%
    timeframe: Mapped[str] = mapped_column(String(64), nullable=False) # Q4 2026
    current: Mapped[str] = mapped_column(String(64), nullable=True)    # +12%
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class StackConfig(Base):
    """Which platforms the company uses — controls which MCPs are active."""
    __tablename__ = "stack_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, nullable=False)
    # Enabled platforms (booleans)
    use_linkedin: Mapped[bool] = mapped_column(Boolean, default=False)
    use_meta: Mapped[bool] = mapped_column(Boolean, default=False)
    use_ghost: Mapped[bool] = mapped_column(Boolean, default=False)
    use_wordpress: Mapped[bool] = mapped_column(Boolean, default=False)
    use_mailchimp: Mapped[bool] = mapped_column(Boolean, default=False)
    use_sendgrid: Mapped[bool] = mapped_column(Boolean, default=False)
    use_hubspot: Mapped[bool] = mapped_column(Boolean, default=False)
    use_salesforce: Mapped[bool] = mapped_column(Boolean, default=False)
    use_higgsfield: Mapped[bool] = mapped_column(Boolean, default=False)
    use_google_workspace: Mapped[bool] = mapped_column(Boolean, default=False)
    # Search engines to use
    search_tavily: Mapped[bool] = mapped_column(Boolean, default=True)
    search_exa: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class EncryptedKey(Base):
    """Stores API keys encrypted at rest using AES-256. Never returned in plaintext."""
    __tablename__ = "encrypted_keys"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, nullable=False)
    key_name: Mapped[str] = mapped_column(String(128), nullable=False)  # e.g. LINKEDIN_ACCESS_TOKEN
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)  # AES-256 ciphertext
    key_hint: Mapped[str] = mapped_column(String(16), nullable=True)    # last 4 chars for display
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class PolicyHold(Base):
    """Persisted policy holds awaiting CEO approval."""
    __tablename__ = "policy_holds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tool: Mapped[str] = mapped_column(String(128), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False)  # APPROVAL / BLOCKED
    args: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")  # PENDING/APPROVED/BLOCKED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class AgentTask(Base):
    """Real-time task tracking for the TaskBoard UI."""
    __tablename__ = "agent_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    skill: Mapped[str] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="QUEUED")  # QUEUED/RUNNING/DONE/FAILED
    logs: Mapped[list] = mapped_column(JSON, default=list)              # streamed log lines
    retry_count: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class ContentDraft(Base):
    """All agent-generated content before it's published."""
    __tablename__ = "content_drafts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)  # blog/email/linkedin/newsletter/etc
    title: Mapped[str] = mapped_column(String(512), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT")   # DRAFT/APPROVED/SCHEDULED/PUBLISHED
    brand_guardian_score: Mapped[str] = mapped_column(String(32), nullable=True)  # APPROVED/NEEDS_REVISION/REJECTED
    brand_guardian_notes: Mapped[str] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    published_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Experiment(Base):
    """A/B experiment hypothesis and results."""
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    control_variant: Mapped[str] = mapped_column(Text, nullable=True)
    treatment_variant: Mapped[str] = mapped_column(Text, nullable=True)
    success_metric: Mapped[str] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT")  # DRAFT/RUNNING/CONCLUDED/FAILED
    winner: Mapped[str] = mapped_column(String(32), nullable=True)    # CONTROL/TREATMENT/INCONCLUSIVE
    confidence: Mapped[float] = mapped_column(Float, nullable=True)   # statistical confidence 0-1
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Lead(Base):
    """Discovered and enriched leads, scored against the active ICP."""
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name: Mapped[str] = mapped_column(String(256), nullable=True)
    website: Mapped[str] = mapped_column(String(512), nullable=True)
    contact_name: Mapped[str] = mapped_column(String(256), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(256), nullable=True)
    contact_linkedin: Mapped[str] = mapped_column(String(512), nullable=True)
    icp_score: Mapped[float] = mapped_column(Float, nullable=True)     # 0–100
    enrichment_data: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="IDENTIFIED")  # IDENTIFIED/CONTACTED/REPLIED/QUALIFIED/CRM
    source: Mapped[str] = mapped_column(String(128), nullable=True)    # linkedin/web/referral
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class APIUsageLog(Base):
    """Tracks every LLM and external API call for cost monitoring."""
    __tablename__ = "api_usage_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String(64), nullable=False)   # gemini/openai/tavily/etc
    model: Mapped[str] = mapped_column(String(128), nullable=True)
    tokens_in: Mapped[int] = mapped_column(nullable=True)
    tokens_out: Mapped[int] = mapped_column(nullable=True)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=True)
    task_id: Mapped[str] = mapped_column(String, nullable=True)         # linked AgentTask
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
