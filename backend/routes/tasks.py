from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db import get_db_session
from backend.models.company import AgentTask
router = APIRouter(prefix='/api', tags=['tasks'])

@router.get('/tasks')
async def get_tasks(db: AsyncSession = Depends(get_db_session)):
    tasks = (await db.execute(select(AgentTask).order_by(AgentTask.created_at.desc()).limit(50))).scalars().all()
    return [{'id': t.id, 'name': t.name, 'skill': t.skill, 'status': t.status, 'logs': t.logs, 'retry_count': t.retry_count, 'created_at': t.created_at.isoformat()} for t in tasks]
