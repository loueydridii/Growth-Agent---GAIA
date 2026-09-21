"""
backend/routes/chat.py — The real chat endpoint wired to GAIABrain.
Replaces the old if/else keyword matching with actual LLM reasoning.
"""
import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db import get_db_session
from backend.agent.brain import GAIABrain
from backend.models.company import Company, BrandVoice, ICP, CEOGoal, AgentTask, PolicyHold

router = APIRouter(prefix="/api", tags=["chat"])
log = structlog.get_logger()


class ChatCommand(BaseModel):
    command: str


@router.post("/chat")
async def handle_chat_command(
    command: ChatCommand,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Accepts a CEO directive, runs it through the real GAIA brain,
    and returns a structured plan with thought process.
    """
    # Load company context from DB
    company = (await db.execute(select(Company).limit(1))).scalars().first()
    brand = (await db.execute(select(BrandVoice).limit(1))).scalars().first()
    active_icp = (await db.execute(select(ICP).where(ICP.is_active == True).limit(1))).scalars().first()
    active_goal = (await db.execute(select(CEOGoal).where(CEOGoal.is_active == True).limit(1))).scalars().first()

    company_context = {
        "name": company.name if company else "Unknown",
        "website": company.website if company else "",
        "industry": company.industry if company else "",
        "stage": company.stage if company else "",
    }
    brand_voice = {
        "tone": brand.tone if brand else "professional",
        "rules": brand.rules if brand else [],
        "forbidden_phrases": brand.forbidden_phrases if brand else [],
    }
    goal_dict = {
        "metric": active_goal.metric if active_goal else "growth",
        "target": active_goal.target if active_goal else "",
        "timeframe": active_goal.timeframe if active_goal else "",
        "current": active_goal.current if active_goal else "unknown",
    }
    icp_dict = None
    if active_icp:
        icp_dict = {
            "name": active_icp.name,
            "seniority": active_icp.seniority,
            "pain_points": active_icp.pain_points or [],
            "goals": active_icp.goals or [],
        }

    # Run through real GAIA brain
    try:
        brain = GAIABrain()
        result = await brain.think(
            directive=command.command,
            company_context=company_context,
            brand_voice=brand_voice,
            active_goal=goal_dict,
            active_icp=icp_dict,
        )
    except RuntimeError as e:
        # API key not configured
        raise HTTPException(status_code=503, detail=str(e))

    # If any actions require approval, create PolicyHold records in DB
    for plan_item in result.get("plan", []):
        if plan_item.get("requires_approval"):
            hold = PolicyHold(
                tool=plan_item["tool"],
                rationale=f"Agent planned to execute '{plan_item['tool']}' for directive: {command.command}",
                risk_level="APPROVAL",
                args=plan_item.get("args", {}),
                status="PENDING",
            )
            db.add(hold)

    # Create an AgentTask record for tracking
    task = AgentTask(
        name=f"Process: {command.command[:80]}",
        skill="growth-orchestrator",
        status="DONE" if not result["requires_approval"] else "AWAITING_APPROVAL",
        logs=result["thought_process"],
    )
    db.add(task)
    await db.commit()

    log.info("chat.handled", category=result["category"], requires_approval=result["requires_approval"])

    return {
        "status": "received",
        "category": result["category"],
        "command": command.command,
        "thought_process": result["thought_process"],
        "plan": result["plan"],
        "requires_approval": result["requires_approval"],
        "response": result["response_summary"],
    }
