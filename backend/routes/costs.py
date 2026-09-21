from fastapi import APIRouter
from backend.agent.cost_tracker import CostTracker
router = APIRouter(prefix='/api', tags=['costs'])

@router.get('/costs')
async def get_costs(days: int = 30):
    tracker = CostTracker()
    return await tracker.get_summary(days=days)
