from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db import get_db_session, get_graphiti
from backend.models.company import PolicyHold
import structlog
from datetime import datetime, timezone

router = APIRouter(prefix='/api', tags=['approvals'])
log = structlog.get_logger()

@router.get('/approvals')
async def get_approvals(db: AsyncSession = Depends(get_db_session)):
    holds = (await db.execute(select(PolicyHold).where(PolicyHold.status == 'PENDING'))).scalars().all()
    return [{'id': h.id, 'tool': h.tool, 'rationale': h.rationale, 'risk': h.risk_level, 'created_at': h.created_at.isoformat(), 'args': h.args} for h in holds]

@router.post('/approve/{action_id}')
async def approve_action(action_id: str, db: AsyncSession = Depends(get_db_session)):
    hold = (await db.execute(select(PolicyHold).where(PolicyHold.id == action_id))).scalars().first()
    if not hold: return {'error': 'not found'}
    hold.status = 'APPROVED'; hold.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    return {'status': 'approved', 'action_id': action_id}

@router.post('/block/{action_id}')
async def block_action(action_id: str, db: AsyncSession = Depends(get_db_session)):
    hold = (await db.execute(select(PolicyHold).where(PolicyHold.id == action_id))).scalars().first()
    if not hold: return {'error': 'not found'}
    hold.status = 'BLOCKED'; hold.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    return {'status': 'blocked', 'action_id': action_id}
