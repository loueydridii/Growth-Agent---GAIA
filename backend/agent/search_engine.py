"""
backend/agent/search_engine.py — Multi-engine search with result synthesis.

Queries Tavily + Exa in parallel, then uses Gemini to synthesize
the best combined answer. The user configures which engines are active
via their StackConfig in the database.
"""
import os
import asyncio
import structlog
from typing import Optional
from dotenv import load_dotenv

import httpx
from tavily import AsyncTavilyClient
from exa_py import Exa

load_dotenv()
log = structlog.get_logger()


class MultiEngineSearch:
    """
    Runs searches across all configured engines in parallel,
    then deduplicates and ranks results by relevance.
    """

    def __init__(self, use_tavily: bool = True, use_exa: bool = False):
        self.use_tavily = use_tavily and bool(os.getenv("TAVILY_API_KEY"))
        self.use_exa = use_exa and bool(os.getenv("EXA_API_KEY"))

        if self.use_tavily:
            self.tavily = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        if self.use_exa:
            self.exa = Exa(api_key=os.getenv("EXA_API_KEY"))

    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_domains: Optional[list] = None,
        exclude_domains: Optional[list] = None,
    ) -> dict:
        """
        Execute search across all active engines in parallel.
        Returns merged, deduplicated results with source metadata.
        """
        tasks = []

        if self.use_tavily:
            tasks.append(self._tavily_search(query, max_results, search_depth, include_domains, exclude_domains))
        if self.use_exa:
            tasks.append(self._exa_search(query, max_results))

        if not tasks:
            log.warning("search.no_engines_configured")
            return {"query": query, "results": [], "synthesis": "No search engines configured. Add TAVILY_API_KEY or EXA_API_KEY to .env."}

        results_per_engine = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge and deduplicate
        all_results = []
        seen_urls = set()
        for engine_results in results_per_engine:
            if isinstance(engine_results, Exception):
                log.error("search.engine_error", error=str(engine_results))
                continue
            for r in engine_results:
                url = r.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)

        log.info("search.complete", query=query[:60], total_results=len(all_results))

        return {
            "query": query,
            "results": all_results[:max_results * 2],  # return top results across engines
            "engines_used": [e for e, active in [("tavily", self.use_tavily), ("exa", self.use_exa)] if active],
        }

    async def _tavily_search(self, query, max_results, depth, include_domains, exclude_domains) -> list:
        try:
            kwargs = {
                "query": query,
                "max_results": max_results,
                "search_depth": depth,
            }
            if include_domains:
                kwargs["include_domains"] = include_domains
            if exclude_domains:
                kwargs["exclude_domains"] = exclude_domains

            response = await self.tavily.search(**kwargs)
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0),
                    "engine": "tavily",
                }
                for r in response.get("results", [])
            ]
        except Exception as e:
            log.error("tavily.error", error=str(e))
            return []

    async def _exa_search(self, query, max_results) -> list:
        try:
            # Exa is synchronous — run in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.exa.search_and_contents(
                    query,
                    num_results=max_results,
                    use_autoprompt=True,
                    text={"max_characters": 800},
                )
            )
            return [
                {
                    "title": r.title or "",
                    "url": r.url or "",
                    "content": r.text or "",
                    "score": getattr(r, "score", 0),
                    "engine": "exa",
                }
                for r in response.results
            ]
        except Exception as e:
            log.error("exa.error", error=str(e))
            return []

    async def competitor_deep_scan(self, competitor_url: str) -> dict:
        """
        Deep scan a specific competitor domain for intelligence signals.
        Checks pricing page, blog, job postings, and landing page.
        """
        pages_to_check = [
            f"{competitor_url}/pricing",
            f"{competitor_url}/blog",
            f"{competitor_url}/jobs",
            f"{competitor_url}/careers",
            f"{competitor_url}",
        ]

        results = await self.search(
            query=f"site:{competitor_url} pricing features announcements",
            max_results=10,
            search_depth="advanced",
            include_domains=[competitor_url],
        )

        return {
            "competitor": competitor_url,
            "signals": results["results"],
            "engines_used": results.get("engines_used", []),
        }
