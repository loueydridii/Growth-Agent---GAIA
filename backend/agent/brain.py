"""
backend/agent/brain.py — The real GAIA reasoning engine.

Uses Google Gemini with function calling to:
1. Understand a CEO directive
2. Retrieve context from Graphiti memory
3. Plan a structured set of tool calls
4. Return a structured execution plan — not a text response.

API key is loaded from .env only. Never hardcoded.
"""
import os
import json
import structlog
from typing import Optional
from dotenv import load_dotenv

import google.genai as genai
from google.genai import types

from backend.agent.graphiti_client import GraphitiClient
from backend.agent.cost_tracker import CostTracker

load_dotenv()
log = structlog.get_logger()

# ── System prompt — GAIA's identity and operating constraints ────────────────
GAIA_SYSTEM_PROMPT = """
You are GAIA — the Growth AI Agent. You operate as the autonomous brain of a 
Growth Operating System for a single company.

Your role:
- Receive a CEO directive (a measurable growth goal or task)
- Retrieve relevant context from your temporal memory graph
- Plan a precise, ordered set of tool calls to achieve the directive
- Flag any action that requires human approval before execution
- NEVER invent facts — if you don't know something, say "unknown"

Operating Constraints (POLICY):
- AUTO: You may execute immediately (analytics, search, read operations)
- APPROVAL: You MUST pause and surface to the CEO (publishing, CRM writes, emails)
- BLOCKED: You MUST NOT execute under any circumstances (bulk deletes, data exports)

Your output must ALWAYS be a valid JSON object matching the PlanResponse schema.
Never return plain text. Never apologize. Be precise and action-oriented.
"""

# ── Tool definitions for Gemini function calling ──────────────────────────────
TOOL_DEFINITIONS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="search_web",
            description="Search the web using multiple engines (Tavily + Exa) and synthesize results. Use for competitor research, market intelligence, lead finding.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING, description="Search query"),
                    "engines": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="Engines to use: tavily, exa"),
                    "max_results": types.Schema(type=types.Type.INTEGER, description="Max results per engine"),
                },
                required=["query"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_content",
            description="Generate marketing content (blog, email, linkedin_post, newsletter, case_study, faq, glossary, video_script, image_brief) based on brand voice.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "content_type": types.Schema(type=types.Type.STRING),
                    "topic": types.Schema(type=types.Type.STRING),
                    "target_icp": types.Schema(type=types.Type.STRING),
                    "goal": types.Schema(type=types.Type.STRING),
                    "channel": types.Schema(type=types.Type.STRING),
                },
                required=["content_type", "topic"],
            ),
        ),
        types.FunctionDeclaration(
            name="publish_content",
            description="Publish approved content to a channel (linkedin, meta, ghost, wordpress, mailchimp, sendgrid). ALWAYS requires APPROVAL policy.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "content_id": types.Schema(type=types.Type.STRING),
                    "channel": types.Schema(type=types.Type.STRING),
                    "scheduled_at": types.Schema(type=types.Type.STRING, description="ISO 8601 datetime or 'now'"),
                },
                required=["content_id", "channel"],
            ),
        ),
        types.FunctionDeclaration(
            name="find_leads",
            description="Search for and enrich potential leads matching the active ICP. Uses configured search engines + LinkedIn MCP.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING),
                    "icp_name": types.Schema(type=types.Type.STRING),
                    "max_leads": types.Schema(type=types.Type.INTEGER),
                },
                required=["query"],
            ),
        ),
        types.FunctionDeclaration(
            name="scan_competitors",
            description="Scan competitor websites and online presence for intelligence signals (pricing, features, messaging).",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "competitors": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                    "signals": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="pricing, features, messaging, job_postings, ads"),
                },
                required=["competitors"],
            ),
        ),
        types.FunctionDeclaration(
            name="update_memory",
            description="Write a new fact, observation, or learning to the Graphiti temporal memory graph.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "fact": types.Schema(type=types.Type.STRING),
                    "entity_type": types.Schema(type=types.Type.STRING, description="Company, ICP, Competitor, Campaign, Lead, Content, Experiment, Metric"),
                    "confidence": types.Schema(type=types.Type.NUMBER),
                },
                required=["fact"],
            ),
        ),
        types.FunctionDeclaration(
            name="create_experiment",
            description="Formulate an A/B hypothesis, create control and treatment variants, and register the experiment.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "hypothesis": types.Schema(type=types.Type.STRING),
                    "success_metric": types.Schema(type=types.Type.STRING),
                    "control_variant": types.Schema(type=types.Type.STRING),
                    "treatment_variant": types.Schema(type=types.Type.STRING),
                },
                required=["hypothesis", "success_metric"],
            ),
        ),
        types.FunctionDeclaration(
            name="trigger_n8n_workflow",
            description="Trigger a specific n8n automation workflow via webhook.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "workflow_name": types.Schema(type=types.Type.STRING),
                    "payload": types.Schema(type=types.Type.OBJECT),
                },
                required=["workflow_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="repurpose_content",
            description="Take a source piece of content and repurpose it into multiple formats for multiple channels.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "source_content_id": types.Schema(type=types.Type.STRING),
                    "target_formats": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                },
                required=["source_content_id", "target_formats"],
            ),
        ),
    ])
]


class GAIABrain:
    """
    The core LLM reasoning engine. One instance per request.
    Connects to Gemini, injects memory context, and returns a structured plan.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        self.graphiti = GraphitiClient()
        self.cost_tracker = CostTracker()

    async def think(
        self,
        directive: str,
        company_context: dict,
        brand_voice: dict,
        active_goal: dict,
        active_icp: Optional[dict] = None,
    ) -> dict:
        """
        Core reasoning loop. Takes a CEO directive and returns a structured plan.

        Returns:
            {
                "category": str,
                "thought_process": list[str],
                "plan": list[dict],       # ordered tool calls
                "requires_approval": bool,
                "response_summary": str,
            }
        """
        # 1. Retrieve relevant context from Graphiti memory
        memory_context = await self.graphiti.search(directive)
        memory_summary = "\n".join([r.get("fact", "") for r in memory_context[:5]])

        # 2. Build the grounded context injection
        context_block = f"""
COMPANY: {company_context.get('name', 'Unknown')} | {company_context.get('industry', '')} | {company_context.get('stage', '')}
WEBSITE: {company_context.get('website', '')}

ACTIVE CEO GOAL: Grow {active_goal.get('metric', '')} {active_goal.get('target', '')} by {active_goal.get('timeframe', '')} (current: {active_goal.get('current', 'unknown')})

ACTIVE ICP: {active_icp.get('name', 'Not configured') if active_icp else 'Not configured'}
PAIN POINTS: {', '.join(active_icp.get('pain_points', [])) if active_icp else ''}

BRAND TONE: {brand_voice.get('tone', 'professional')}
BRAND RULES: {'; '.join(brand_voice.get('rules', []))}
FORBIDDEN: {', '.join(brand_voice.get('forbidden_phrases', []))}

RELEVANT MEMORY:
{memory_summary if memory_summary else 'No prior context found for this directive.'}
"""

        # 3. Call Gemini with function calling enabled
        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=GAIA_SYSTEM_PROMPT + "\n\nCurrent Context:\n" + context_block,
                tools=TOOL_DEFINITIONS,
                temperature=0.3,
                response_mime_type="application/json",
            ),
            contents=[directive],
        )

        # 4. Track cost
        if response.usage_metadata:
            await self.cost_tracker.log(
                provider="gemini",
                model=self.model,
                tokens_in=response.usage_metadata.prompt_token_count or 0,
                tokens_out=response.usage_metadata.candidates_token_count or 0,
            )

        # 5. Parse the structured plan from function calls
        plan = []
        requires_approval = False

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    tool_name = part.function_call.name
                    tool_args = dict(part.function_call.args)

                    # Approval-required tools
                    if tool_name in ("publish_content", "trigger_n8n_workflow"):
                        requires_approval = True

                    plan.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "requires_approval": tool_name in ("publish_content", "trigger_n8n_workflow"),
                    })

        # 6. Build thought process summary
        thought_process = [
            f"[Observe] Directive received: '{directive}'",
            f"[Memory] Retrieved {len(memory_context)} relevant facts from Graphiti",
            f"[Context] Active goal: {active_goal.get('metric', '')} {active_goal.get('target', '')}",
            f"[Plan] Gemini generated {len(plan)} tool call(s)",
        ]
        if requires_approval:
            thought_process.append("[Policy] One or more actions require CEO approval — halting auto-execution")

        # 7. Generate summary text from the response
        response_text = ""
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text:
                    response_text += part.text

        return {
            "category": self._classify(directive),
            "thought_process": thought_process,
            "plan": plan,
            "requires_approval": requires_approval,
            "response_summary": response_text or self._default_summary(directive, plan),
        }

    def _classify(self, directive: str) -> str:
        d = directive.lower()
        if any(k in d for k in ["grow", "increase", "pipeline", "revenue", "leads"]):
            return "CEO_GOAL"
        elif any(k in d for k in ["competitor", "market", "scan", "intelligence"]):
            return "OPPORTUNITY_SCAN"
        elif any(k in d for k in ["write", "blog", "email", "post", "newsletter", "content"]):
            return "CONTENT"
        elif any(k in d for k in ["experiment", "test", "hypothesis", "a/b"]):
            return "EXPERIMENT"
        elif any(k in d for k in ["lead", "prospect", "find", "enrich"]):
            return "LEAD_GEN"
        return "GENERAL"

    def _default_summary(self, directive: str, plan: list) -> str:
        tools = ", ".join([p["tool"] for p in plan]) if plan else "none"
        return f"I have received your directive and planned {len(plan)} action(s) using: {tools}."
