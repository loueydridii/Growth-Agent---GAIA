from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
import httpx
import asyncio

app = FastAPI(title="GAIA Command Center API", version="1.0.0")

# Enable CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory state (replace with Postgres in production) ──────────────────
_approvals: list[dict] = [
    {"id": "act_1", "tool": "publish_post", "rationale": "Publish Q3 recap on LinkedIn to drive inbound.", "risk": "APPROVAL", "created_at": "2026-09-20T18:00:00Z"},
    {"id": "act_2", "tool": "delete_crm_data", "rationale": "Prune 500 bounced emails from CRM to improve deliverability.", "risk": "BLOCKED", "created_at": "2026-09-20T19:00:00Z"},
]

_memory_nodes: list[dict] = [
    {"id": "n1", "source": "Company: ACME", "target": "ICP: Enterprise DevOps", "relation": "TARGETS"},
    {"id": "n2", "source": "ICP: Enterprise DevOps", "target": "Problem: Slow CI/CD", "relation": "HAS_PROBLEM"},
    {"id": "n3", "source": "Campaign: Q3 DevOps Push", "target": "Problem: Slow CI/CD", "relation": "ADDRESSES"},
    {"id": "n4", "source": "Competitor: BuildFast", "target": "ICP: Enterprise DevOps", "relation": "ALSO_TARGETS"},
    {"id": "n5", "source": "Content: CI/CD Guide", "target": "Campaign: Q3 DevOps Push", "relation": "SUPPORTS"},
]

_active_goal: dict = {
    "metric": "pipeline",
    "target": "+30%",
    "timeframe": "Q4 2026",
    "current": "+12%"
}

_agent_config: dict = {
    "n8n_url": "http://localhost:5678",
    "n8n_api_key": "",
    "model": "Growth Orchestrator v1 (GAIA)"
}

# ── Models ──────────────────────────────────────────────────────────────────
class ChatCommand(BaseModel):
    command: str

class AgentConfig(BaseModel):
    n8n_url: Optional[str] = None
    n8n_api_key: Optional[str] = None
    goal_metric: Optional[str] = None
    goal_target: Optional[str] = None
    goal_timeframe: Optional[str] = None


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {"status": "ok", "agent": "GAIA", "version": "1.0.0"}

@app.get("/api/status")
def get_status():
    """Returns full agent brain status."""
    return {
        "agent_name": "GAIA",
        "full_name": "Growth AI Agent",
        "model": _agent_config["model"],
        "active_goal": _active_goal,
        "skills": [
            "growth-orchestrator",
            "agent-planner",
            "evidence-verification",
            "graphiti-memory",
            "growth-strategy",
            "decision-engine",
        ],
        "online": True,
    }

@app.post("/api/chat")
async def handle_chat_command(command: ChatCommand):
    """
    Accepts a CEO directive and routes it through the GAIA brain.
    Currently returns a structured thought-process response.
    In production, this spawns the growth-orchestrator subprocess.
    """
    cmd = command.command.lower()

    # Simple routing rules (mirrors the growth-orchestrator SKILL)
    if any(k in cmd for k in ["grow", "increase", "pipeline", "leads", "revenue"]):
        category = "CEO_GOAL"
        thought_process = [
            f"[Observe] Checking active goal: Grow {_active_goal['metric']} {_active_goal['target']} by {_active_goal['timeframe']}",
            f"[Verify] Cross-checking claim against evidence engine...",
            f"[Plan] Invoking agent-planner — breaking objective into dependency graph",
            f"[Decide] Checking Tool Registry policies for planned actions...",
            f"[Approve Needed] 'publish_post' flagged as APPROVAL — added to Policy Holds",
        ]
        response = (
            f"Objective received. I am optimising for: **{_active_goal['metric']} {_active_goal['target']}** by {_active_goal['timeframe']} "
            f"(current progress: {_active_goal['current']}). "
            f"I have generated a 5-step execution plan. The action 'publish_post' requires your manual approval — check Policy Holds."
        )
    elif any(k in cmd for k in ["competitor", "market", "analyse", "scan"]):
        category = "OPPORTUNITY_SCAN"
        thought_process = [
            "[Observe] Fetching competitor intelligence from Graphiti memory...",
            "[Verify] Running evidence engine on competitor claims...",
            "[Plan] Running opportunity_scanner.py against known signals...",
            "[Decide] Signal scored [ACTIONABLE] — Impact: 0.8, Confidence: 0.7",
        ]
        response = (
            "Opportunity scan complete. I found 2 actionable signals: "
            "(1) Competitor BuildFast dropped pricing — ICP Enterprise DevOps is reconsidering. "
            "(2) Search volume for 'CI/CD automation' up 34% this month. "
            "Recommended action: Publish a comparison piece and update LinkedIn targeting."
        )
    elif any(k in cmd for k in ["experiment", "test", "hypothesis", "a/b"]):
        category = "EXPERIMENT"
        thought_process = [
            "[Observe] Checking experiment_engine.py for existing hypotheses...",
            "[Plan] Formulating new hypothesis from objective...",
            "[Decide] Creating EXP-draft — awaiting your approval to run",
        ]
        response = (
            "Hypothesis formulated: 'If we add a free CI/CD benchmark tool to our landing page, "
            "then demo requests will increase by 15% because it addresses the top ICP concern.' "
            "I have created EXP-draft in the Experiment Engine. Variants: A (Control) vs B (Treatment: +Tool). "
            "Shall I proceed?"
        )
    else:
        category = "GENERAL"
        thought_process = [
            "[Observe] Parsing directive...",
            "[Context] Loading ICP definitions and active campaign context from Graphiti...",
            "[Plan] Routing to relevant specialist skill...",
        ]
        response = (
            f"I have received your directive: '{command.command}'. "
            "I am processing this through the growth-orchestrator. "
            "To activate CEO Mode, try phrasing your goal as: 'Grow [metric] by [target] in [timeframe]'."
        )

    return {
        "status": "received",
        "category": category,
        "command": command.command,
        "thought_process": thought_process,
        "response": response,
    }


@app.get("/api/approvals")
def get_pending_approvals():
    return _approvals

@app.post("/api/approve/{action_id}")
def approve_action(action_id: str):
    global _approvals
    action = next((a for a in _approvals if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    _approvals = [a for a in _approvals if a["id"] != action_id]
    return {"status": "approved", "action_id": action_id}

@app.post("/api/block/{action_id}")
def block_action(action_id: str):
    global _approvals
    action = next((a for a in _approvals if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    _approvals = [a for a in _approvals if a["id"] != action_id]
    return {"status": "blocked", "action_id": action_id}

@app.get("/api/memory")
def get_graph_memory():
    return _memory_nodes

@app.get("/api/workflows")
async def get_workflows():
    """
    Fetches live workflow data from the local n8n instance.
    Falls back to mock data if n8n is not reachable.
    """
    n8n_url = _agent_config.get("n8n_url", "http://localhost:5678")
    api_key = _agent_config.get("n8n_api_key", "")

    if api_key:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(
                    f"{n8n_url}/api/v1/workflows",
                    headers={"X-N8N-API-KEY": api_key}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {"source": "live", "workflows": data.get("data", [])}
        except Exception:
            pass  # Fall through to mock

    # Mock data when n8n is unreachable or no API key
    return {
        "source": "mock",
        "workflows": [
            {"id": "wf_1", "name": "LinkedIn Lead Scraper", "active": True, "updatedAt": "2026-09-20T18:00:00Z", "tags": ["leads"]},
            {"id": "wf_2", "name": "SEO Weekly Report", "active": True, "updatedAt": "2026-09-20T12:00:00Z", "tags": ["seo"]},
            {"id": "wf_3", "name": "Competitor Price Monitor", "active": False, "updatedAt": "2026-09-19T10:00:00Z", "tags": ["intel"]},
            {"id": "wf_4", "name": "CRM Enrichment", "active": True, "updatedAt": "2026-09-20T17:30:00Z", "tags": ["crm"]},
        ]
    }

@app.get("/api/goal")
def get_goal():
    return _active_goal

@app.post("/api/settings")
def update_settings(config: AgentConfig):
    global _agent_config, _active_goal
    if config.n8n_url:
        _agent_config["n8n_url"] = config.n8n_url
    if config.n8n_api_key is not None:
        _agent_config["n8n_api_key"] = config.n8n_api_key
    if config.goal_metric:
        _active_goal["metric"] = config.goal_metric
    if config.goal_target:
        _active_goal["target"] = config.goal_target
    if config.goal_timeframe:
        _active_goal["timeframe"] = config.goal_timeframe
    return {"status": "ok", "config": _agent_config, "goal": _active_goal}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
