import os, httpx, structlog
from fastapi import APIRouter
from dotenv import load_dotenv
load_dotenv()
router = APIRouter(prefix='/api', tags=['workflows'])
log = structlog.get_logger()

@router.get('/workflows')
async def get_workflows():
    n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
    api_key = os.getenv('N8N_API_KEY', '')
    if api_key:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f'{n8n_url}/api/v1/workflows', headers={'X-N8N-API-KEY': api_key})
                if resp.status_code == 200:
                    return {'source': 'live', 'workflows': resp.json().get('data', [])}
        except Exception: pass
    return {'source': 'mock', 'workflows': [
        {'id': 'wf_1', 'name': 'LinkedIn Lead Scraper', 'active': True, 'updatedAt': '2026-09-21T18:00:00Z', 'tags': ['leads']},
        {'id': 'wf_2', 'name': 'SEO Weekly Report', 'active': True, 'updatedAt': '2026-09-21T12:00:00Z', 'tags': ['seo']},
        {'id': 'wf_3', 'name': 'Competitor Price Monitor', 'active': False, 'updatedAt': '2026-09-20T10:00:00Z', 'tags': ['intel']},
        {'id': 'wf_4', 'name': 'CRM Enrichment', 'active': True, 'updatedAt': '2026-09-21T17:30:00Z', 'tags': ['crm']},
        {'id': 'wf_5', 'name': 'Daily Digest Builder', 'active': True, 'updatedAt': '2026-09-21T09:00:00Z', 'tags': ['digest']},
        {'id': 'wf_6', 'name': 'Blog Publisher (Ghost)', 'active': False, 'updatedAt': '2026-09-19T14:00:00Z', 'tags': ['content']},
    ]}
