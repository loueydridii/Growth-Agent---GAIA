import structlog
from fastapi import APIRouter
from backend.agent.search_engine import MultiEngineSearch
router = APIRouter(prefix='/api', tags=['intelligence'])
log = structlog.get_logger()

@router.get('/intelligence/search')
async def search(q: str, engines: str = 'tavily'):
    use_exa = 'exa' in engines
    searcher = MultiEngineSearch(use_tavily='tavily' in engines, use_exa=use_exa)
    return await searcher.search(q)

@router.get('/intelligence/competitor')
async def scan_competitor(url: str):
    searcher = MultiEngineSearch(use_tavily=True, use_exa=False)
    return await searcher.competitor_deep_scan(url)
