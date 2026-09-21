"""
backend/agent/brand_guardian.py — Brand compliance enforcement layer.

Every piece of generated content MUST pass through Brand Guardian
before it can be scheduled or published. Returns APPROVED, NEEDS_REVISION, or REJECTED.
"""
import os
import json
import structlog
from dotenv import load_dotenv

import google.genai as genai
from google.genai import types
from backend.agent.cost_tracker import CostTracker

load_dotenv()
log = structlog.get_logger()

GUARDIAN_SYSTEM = """You are the Brand Guardian for a marketing team.
Your job is to review generated content against the brand voice guidelines and return a structured JSON verdict.

You must check for:
1. Tone alignment — does it match the specified tone (professional/casual/bold/technical)?
2. Rule compliance — does it follow all writing rules?
3. Forbidden phrases — does it contain any forbidden words or phrases?
4. Factual claims — flag any unverified statistics or bold claims (mark as UNVERIFIED)
5. Brand differentiation — does it sound generic or distinctly on-brand?

Return ONLY valid JSON in this exact structure:
{
  "verdict": "APPROVED" | "NEEDS_REVISION" | "REJECTED",
  "score": 0-100,
  "issues": [{"type": "tone|rule|forbidden|factual|generic", "line": "...", "suggestion": "..."}],
  "summary": "One sentence verdict explanation"
}"""


class BrandGuardian:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")

        self.client = genai.Client(api_key=api_key)
        # Use the faster model for Guardian passes — saves cost
        self.model = "gemini-2.0-flash"
        self.cost_tracker = CostTracker()

    async def review(
        self,
        content: str,
        content_type: str,
        brand_voice: dict,
    ) -> dict:
        """
        Review content against brand guidelines.
        Returns structured verdict with annotations.
        """
        guidelines_block = f"""
Brand Voice Rules:
- Tone: {brand_voice.get('tone', 'professional')}
- Writing rules: {'; '.join(brand_voice.get('rules', []))}
- NEVER use these phrases: {', '.join(brand_voice.get('forbidden_phrases', ['guaranteed', 'best in class', 'world-class']))}
- Content type: {content_type}
"""

        review_prompt = f"""{guidelines_block}

Content to review:
---
{content[:3000]}
---

Return your structured JSON verdict now."""

        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=GUARDIAN_SYSTEM,
                temperature=0.1,
                response_mime_type="application/json",
            ),
            contents=[review_prompt],
        )

        if response.usage_metadata:
            await self.cost_tracker.log(
                provider="gemini",
                model=self.model,
                tokens_in=response.usage_metadata.prompt_token_count or 0,
                tokens_out=response.usage_metadata.candidates_token_count or 0,
                call_type="brand_guardian",
            )

        try:
            result_text = response.candidates[0].content.parts[0].text
            result = json.loads(result_text)
        except Exception as e:
            log.error("brand_guardian.parse_failed", error=str(e))
            result = {
                "verdict": "NEEDS_REVISION",
                "score": 50,
                "issues": [{"type": "system", "line": "", "suggestion": "Brand Guardian could not parse response. Manual review required."}],
                "summary": "Automated review failed — manual review required.",
            }

        log.info("brand_guardian.reviewed", content_type=content_type, verdict=result.get("verdict"), score=result.get("score"))
        return result
