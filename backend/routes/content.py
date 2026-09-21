from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db import get_db_session
from backend.models.company import ContentDraft, BrandVoice
from backend.agent.content_engine import ContentEngine
from backend.agent.brand_guardian import BrandGuardian
import structlog

router = APIRouter(prefix='/api', tags=['content'])
log = structlog.get_logger()

class ContentRequest(BaseModel):
    content_type: str
    topic: str
    channel: Optional[str] = None
    goal: Optional[str] = None

@router.post('/content/generate')
async def generate_content(req: ContentRequest, db: AsyncSession = Depends(get_db_session)):
    brand = (await db.execute(select(BrandVoice).limit(1))).scalars().first()
    brand_voice = {'tone': brand.tone if brand else 'professional', 'rules': brand.rules if brand else [], 'forbidden_phrases': brand.forbidden_phrases if brand else []}
    engine = ContentEngine()
    result = await engine.generate(req.content_type, req.topic, brand_voice, channel=req.channel, goal=req.goal)
    guardian = BrandGuardian()
    verdict = await guardian.review(result['body'], req.content_type, brand_voice)
    draft = ContentDraft(content_type=result['content_type'], title=result['title'], body=result['body'], channel=result.get('channel', req.content_type), status='DRAFT', brand_guardian_score=verdict['verdict'], brand_guardian_notes=str(verdict.get('issues', [])))
    db.add(draft); await db.commit()
    return {'id': draft.id, **result, 'brand_guardian': verdict}

@router.get('/content/drafts')
async def get_drafts(db: AsyncSession = Depends(get_db_session)):
    drafts = (await db.execute(select(ContentDraft).order_by(ContentDraft.created_at.desc()).limit(50))).scalars().all()
    return [{'id': d.id, 'content_type': d.content_type, 'title': d.title, 'channel': d.channel, 'status': d.status, 'brand_guardian_score': d.brand_guardian_score, 'scheduled_at': d.scheduled_at.isoformat() if d.scheduled_at else None, 'created_at': d.created_at.isoformat()} for d in drafts]

@router.post('/content/{draft_id}/approve')
async def approve_draft(draft_id: str, db: AsyncSession = Depends(get_db_session)):
    draft = (await db.execute(select(ContentDraft).where(ContentDraft.id == draft_id))).scalars().first()
    if not draft: return {'error': 'not found'}
    draft.status = 'APPROVED'; await db.commit()
    return {'status': 'ok', 'id': draft_id}
