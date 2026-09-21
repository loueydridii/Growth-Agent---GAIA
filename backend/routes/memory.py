from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db import get_db_session
from backend.agent.graphiti_client import GraphitiClient
import structlog

router = APIRouter(prefix='/api', tags=['memory'])
log = structlog.get_logger()

@router.get('/memory')
async def get_memory():
    try:
        g = GraphitiClient()
        return await g.get_nodes_for_ui()
    except Exception as e:
        log.warning('memory.error', error=str(e))
        return [
            {'id': 'n1', 'source': 'Company: GAIA Demo', 'target': 'ICP: Growth Teams', 'relation': 'TARGETS'},
            {'id': 'n2', 'source': 'ICP: Growth Teams', 'target': 'Problem: Manual Reporting', 'relation': 'HAS_PROBLEM'},
        ]
