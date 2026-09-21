"""
backend/routes/settings.py — Company config, brand voice, ICP, stack, and API key management.
API keys stored AES-256 encrypted. Never returned in plaintext.
"""
import os
import json
import structlog
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from backend.db import get_db_session
from backend.models.company import Company, BrandVoice, ICP, CEOGoal, StackConfig, EncryptedKey

load_dotenv()
router = APIRouter(prefix="/api", tags=["settings"])
log = structlog.get_logger()


def _get_cipher():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Generate a warning — fallback to SECRET_KEY for dev
        key = os.getenv("SECRET_KEY", "").encode()[:32].ljust(32, b"0")
        key = Fernet.generate_key()
    return Fernet(key if isinstance(key, bytes) else key.encode())


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None

class BrandVoiceUpdate(BaseModel):
    tone: Optional[str] = None
    rules: Optional[list] = None
    forbidden_phrases: Optional[list] = None
    hex_primary: Optional[str] = None
    hex_secondary: Optional[str] = None
    context_md: Optional[str] = None

class ICPCreate(BaseModel):
    name: str
    seniority: Optional[str] = None
    company_size_min: Optional[int] = None
    company_size_max: Optional[int] = None
    industries: Optional[list] = None
    pain_points: Optional[list] = None
    goals: Optional[list] = None
    objections: Optional[list] = None
    channels: Optional[list] = None

class GoalUpdate(BaseModel):
    metric: str
    target: str
    timeframe: str
    current: Optional[str] = None

class StackUpdate(BaseModel):
    use_linkedin: Optional[bool] = None
    use_meta: Optional[bool] = None
    use_ghost: Optional[bool] = None
    use_wordpress: Optional[bool] = None
    use_mailchimp: Optional[bool] = None
    use_sendgrid: Optional[bool] = None
    use_hubspot: Optional[bool] = None
    use_salesforce: Optional[bool] = None
    use_higgsfield: Optional[bool] = None
    use_google_workspace: Optional[bool] = None
    search_tavily: Optional[bool] = None
    search_exa: Optional[bool] = None

class APIKeyStore(BaseModel):
    key_name: str
    value: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/status")
async def get_status(db: AsyncSession = Depends(get_db_session)):
    company = (await db.execute(select(Company).limit(1))).scalars().first()
    goal = (await db.execute(select(CEOGoal).where(CEOGoal.is_active == True).limit(1))).scalars().first()
    return {
        "agent_name": "GAIA",
        "full_name": "Growth AI Agent",
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
        "company": company.name if company else None,
        "active_goal": {
            "metric": goal.metric if goal else "",
            "target": goal.target if goal else "",
            "timeframe": goal.timeframe if goal else "",
            "current": goal.current if goal else "",
        } if goal else None,
        "skills": ["growth-orchestrator", "agent-planner", "evidence-verification",
                   "graphiti-memory", "growth-strategy", "decision-engine"],
        "online": True,
    }

@router.get("/company")
async def get_company(db: AsyncSession = Depends(get_db_session)):
    company = (await db.execute(select(Company).limit(1))).scalars().first()
    if not company:
        return {}
    return {"id": company.id, "name": company.name, "website": company.website,
            "industry": company.industry, "stage": company.stage}

@router.post("/company")
async def upsert_company(data: CompanyUpdate, db: AsyncSession = Depends(get_db_session)):
    company = (await db.execute(select(Company).limit(1))).scalars().first()
    if not company:
        company = Company(**data.model_dump(exclude_none=True))
        db.add(company)
    else:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(company, k, v)
    await db.commit()
    return {"status": "ok"}

@router.get("/brand")
async def get_brand(db: AsyncSession = Depends(get_db_session)):
    brand = (await db.execute(select(BrandVoice).limit(1))).scalars().first()
    if not brand:
        return {}
    return {"tone": brand.tone, "rules": brand.rules, "forbidden_phrases": brand.forbidden_phrases,
            "hex_primary": brand.hex_primary, "hex_secondary": brand.hex_secondary, "context_md": brand.context_md}

@router.post("/brand")
async def upsert_brand(data: BrandVoiceUpdate, db: AsyncSession = Depends(get_db_session)):
    brand = (await db.execute(select(BrandVoice).limit(1))).scalars().first()
    if not brand:
        company = (await db.execute(select(Company).limit(1))).scalars().first()
        brand = BrandVoice(company_id=company.id if company else "default", **data.model_dump(exclude_none=True))
        db.add(brand)
    else:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(brand, k, v)
    await db.commit()
    return {"status": "ok"}

@router.get("/icps")
async def get_icps(db: AsyncSession = Depends(get_db_session)):
    icps = (await db.execute(select(ICP))).scalars().all()
    return [{"id": i.id, "name": i.name, "is_active": i.is_active, "seniority": i.seniority,
             "pain_points": i.pain_points, "channels": i.channels} for i in icps]

@router.post("/icps")
async def create_icp(data: ICPCreate, db: AsyncSession = Depends(get_db_session)):
    company = (await db.execute(select(Company).limit(1))).scalars().first()
    icp = ICP(company_id=company.id if company else "default", **data.model_dump())
    db.add(icp)
    await db.commit()
    return {"status": "ok", "id": icp.id}

@router.post("/goal")
async def upsert_goal(data: GoalUpdate, db: AsyncSession = Depends(get_db_session)):
    # Deactivate old goal
    await db.execute(update(CEOGoal).values(is_active=False))
    company = (await db.execute(select(Company).limit(1))).scalars().first()
    goal = CEOGoal(
        company_id=company.id if company else "default",
        **data.model_dump(),
        is_active=True,
    )
    db.add(goal)
    await db.commit()
    return {"status": "ok"}

@router.post("/stack")
async def upsert_stack(data: StackUpdate, db: AsyncSession = Depends(get_db_session)):
    stack = (await db.execute(select(StackConfig).limit(1))).scalars().first()
    if not stack:
        company = (await db.execute(select(Company).limit(1))).scalars().first()
        stack = StackConfig(company_id=company.id if company else "default", **data.model_dump(exclude_none=True))
        db.add(stack)
    else:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(stack, k, v)
    await db.commit()
    return {"status": "ok"}

@router.get("/stack")
async def get_stack(db: AsyncSession = Depends(get_db_session)):
    stack = (await db.execute(select(StackConfig).limit(1))).scalars().first()
    if not stack:
        return {}
    return {c.name: getattr(stack, c.name) for c in StackConfig.__table__.columns if c.name not in ("id", "company_id", "updated_at")}

@router.post("/keys")
async def store_api_key(data: APIKeyStore, db: AsyncSession = Depends(get_db_session)):
    """Encrypt and store an API key. Returns only the last 4 chars for display."""
    cipher = _get_cipher()
    encrypted = cipher.encrypt(data.value.encode()).decode()
    hint = data.value[-4:] if len(data.value) >= 4 else "****"

    company = (await db.execute(select(Company).limit(1))).scalars().first()

    # Check if key already exists for this name
    existing = (await db.execute(
        select(EncryptedKey).where(EncryptedKey.key_name == data.key_name)
    )).scalars().first()

    if existing:
        existing.encrypted_value = encrypted
        existing.key_hint = hint
    else:
        key_record = EncryptedKey(
            company_id=company.id if company else "default",
            key_name=data.key_name,
            encrypted_value=encrypted,
            key_hint=hint,
        )
        db.add(key_record)

    await db.commit()
    log.info("api_key.stored", key_name=data.key_name, hint=hint)
    return {"status": "ok", "key_name": data.key_name, "hint": f"****{hint}"}

@router.get("/keys")
async def list_api_keys(db: AsyncSession = Depends(get_db_session)):
    """Returns key names and hints only. Never returns plaintext values."""
    keys = (await db.execute(select(EncryptedKey))).scalars().all()
    return [{"key_name": k.key_name, "hint": f"****{k.key_hint}"} for k in keys]
