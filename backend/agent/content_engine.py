"""
backend/agent/content_engine.py — LLM-powered content factory.

Generates all marketing content types with brand voice injection.
All outputs are routed through Brand Guardian before storage.
API key loaded from .env only.
"""
import os
import structlog
from typing import Optional
from dotenv import load_dotenv

import google.genai as genai
from google.genai import types

from backend.agent.cost_tracker import CostTracker

load_dotenv()
log = structlog.get_logger()

CONTENT_PROMPTS = {
    "blog": """Write a comprehensive SEO-optimized blog post. Include:
- Attention-grabbing H1 title
- Meta description (150-160 chars)
- Introduction with a hook that speaks directly to the pain point
- 3-5 H2 sections with practical insights
- A clear CTA at the end
- Naturally integrated keywords
Format: Markdown""",

    "newsletter": """Write a compelling newsletter edition. Include:
- Subject line with high open-rate hook
- Preview text (preheader)
- Opening insight or story (2-3 sentences)
- 3 key points/links with brief explanations
- One clear CTA
- Warm sign-off
Keep it under 400 words. Format: Markdown""",

    "email_sequence": """Write a 3-touch cold outreach email sequence. For each email include:
- Subject line
- Opening line (personalized, no 'I hope this finds you well')
- Body (max 100 words, focused on ONE value prop)
- CTA (specific ask)
- Timing note (e.g., 'Day 1', 'Day 3', 'Day 7')
Format: Markdown""",

    "linkedin_post": """Write a LinkedIn post. Structure:
- Hook line (stops the scroll — question, bold claim, or unexpected stat)
- 3-4 short paragraphs (insights, story, or data)
- CTA or question to drive comments
- 3-5 relevant hashtags
Max 250 words. Use line breaks generously for mobile readability.""",

    "instagram_caption": """Write an Instagram caption. Include:
- First line hook (visible before 'more')
- 2-3 lines of value/story
- CTA
- Line break then: 20-25 hashtags (mix of broad, niche, branded)
Keep the above-fold portion under 125 characters.""",

    "case_study": """Write a full case study. Structure:
- Client overview (anonymize if needed)
- The Challenge (specific pain point and business impact)
- The Solution (what was implemented, step by step)
- The Results (quantified outcomes — use numbers)
- Quote from stakeholder
- Key takeaways
Format: Markdown with clear H2/H3 hierarchy.""",

    "faq": """Generate a comprehensive FAQ based on the topic and ICP pain points.
- Include 8-12 questions
- Each answer: 50-100 words, conversational, direct
- Structure for AEO (Answer Engine Optimization — how AI search engines find answers)
- Include 1-2 long-tail questions that prospects actually search for
Format: Markdown with H3 for each question.""",

    "glossary": """Create a brand-owned glossary entry for the given term. Include:
- Clear definition (1-2 sentences)
- Why it matters for the ICP
- How your approach differs from the standard definition (brand differentiation)
- 2-3 related terms (with brief links)
Format: Markdown""",

    "video_script": """Write a video script. Include:
- Hook (first 3 seconds — must stop thumb-scrolling)
- Scene-by-scene breakdown
- Voiceover/on-screen text for each scene
- B-roll suggestions
- CTA (last 5 seconds)
Specify duration: 60s / 90s / 180s""",

    "image_brief": """Write a detailed visual brief for AI image generation. Include:
- Subject description (what/who is in the image)
- Composition and framing
- Color palette (reference brand hex codes)
- Mood and lighting
- Style (photorealistic / illustration / 3D / abstract)
- Negative prompts (what to avoid)
Format this as a Higgsfield/DALL-E compatible prompt.""",

    "video_prompt": """Write a Higgsfield AI video generation prompt. Include:
- Scene description (camera movement, subject, environment)
- Style (cinematic / documentary / product)
- Duration hint
- Motion dynamics (slow pan / tracking shot / static)
- Lighting and mood
Follow Higgsfield's prompt format for best results.""",
}


class ContentEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        self.cost_tracker = CostTracker()

    async def generate(
        self,
        content_type: str,
        topic: str,
        brand_voice: dict,
        icp: Optional[dict] = None,
        goal: Optional[str] = None,
        channel: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> dict:
        """
        Generate a piece of marketing content.
        Returns: { content_type, title, body, channel, brand_guardian_pending: True }
        """
        if content_type not in CONTENT_PROMPTS:
            raise ValueError(f"Unknown content type: {content_type}. Valid: {list(CONTENT_PROMPTS.keys())}")

        # Build the brand-grounded prompt
        brand_block = f"""
BRAND VOICE: {brand_voice.get('tone', 'professional')}
WRITING RULES: {'; '.join(brand_voice.get('rules', ['Be concise', 'Use active voice']))}
NEVER SAY: {', '.join(brand_voice.get('forbidden_phrases', []))}
PRIMARY COLOR: {brand_voice.get('hex_primary', '#000000')}
"""

        icp_block = ""
        if icp:
            icp_block = f"""
TARGET READER:
- Role/Seniority: {icp.get('seniority', '')}
- Company Size: {icp.get('company_size_min', '')}-{icp.get('company_size_max', '')} employees
- Pain Points: {', '.join(icp.get('pain_points', []))}
- Goals: {', '.join(icp.get('goals', []))}
"""

        system_prompt = f"""You are a world-class B2B marketing copywriter.
{brand_block}
{icp_block}
{'Context goal: ' + goal if goal else ''}
{'Additional context: ' + additional_context if additional_context else ''}

{CONTENT_PROMPTS[content_type]}

Write now for topic: {topic}"""

        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            ),
            contents=[f"Create this content: {topic}"],
        )

        body = ""
        if response.candidates and response.candidates[0].content.parts:
            body = response.candidates[0].content.parts[0].text or ""

        # Track cost
        if response.usage_metadata:
            await self.cost_tracker.log(
                provider="gemini",
                model=self.model,
                tokens_in=response.usage_metadata.prompt_token_count or 0,
                tokens_out=response.usage_metadata.candidates_token_count or 0,
                call_type=f"content_{content_type}",
            )

        # Extract title if it's the first line
        lines = body.strip().split("\n")
        title = lines[0].lstrip("#").strip() if lines else topic

        log.info("content.generated", content_type=content_type, topic=topic[:60], chars=len(body))

        return {
            "content_type": content_type,
            "title": title,
            "body": body,
            "channel": channel or content_type,
            "status": "DRAFT",
            "brand_guardian_pending": True,  # Must pass Brand Guardian before scheduling
        }

    async def repurpose(
        self,
        source_body: str,
        source_type: str,
        target_formats: list[str],
        brand_voice: dict,
        icp: Optional[dict] = None,
    ) -> list[dict]:
        """
        Repurpose a single piece of content into multiple formats.
        The time-saving power move for marketing teams.
        """
        results = []
        for target_type in target_formats:
            log.info("content.repurposing", source=source_type, target=target_type)

            repurpose_prompt = f"""You are adapting existing {source_type} content for a new format.
Original content:
---
{source_body[:2000]}
---
Now adapt this into: {target_type.upper()}
Preserve the key insights and brand voice. Adjust length, tone, and format for the new channel."""

            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=f"Brand voice: {brand_voice.get('tone', 'professional')}. Rules: {'; '.join(brand_voice.get('rules', []))}",
                    temperature=0.6,
                ),
                contents=[repurpose_prompt],
            )

            body = ""
            if response.candidates and response.candidates[0].content.parts:
                body = response.candidates[0].content.parts[0].text or ""

            if response.usage_metadata:
                await self.cost_tracker.log(
                    provider="gemini",
                    model=self.model,
                    tokens_in=response.usage_metadata.prompt_token_count or 0,
                    tokens_out=response.usage_metadata.candidates_token_count or 0,
                    call_type=f"repurpose_{target_type}",
                )

            results.append({
                "content_type": target_type,
                "body": body,
                "status": "DRAFT",
                "brand_guardian_pending": True,
                "repurposed_from": source_type,
            })

        return results
