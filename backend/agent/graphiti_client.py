"""
backend/agent/graphiti_client.py — Wrapper around the Graphiti Neo4j temporal graph.
All credentials loaded from .env exclusively.
"""
import os
import structlog
from typing import Optional
from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

load_dotenv()
log = structlog.get_logger()

ENTITY_TYPES = [
    "Company", "ICP", "Competitor", "Campaign",
    "Lead", "Content", "Experiment", "Metric", "Decision"
]


class GraphitiClient:
    """
    Temporal knowledge graph client.
    Wraps graphiti-core for GAIA-specific operations.
    """

    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            raise RuntimeError("NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD must be set in .env")

        self._client = Graphiti(
            neo4j_uri=uri,
            neo4j_user=user,
            neo4j_password=password,
        )

    async def initialize(self):
        """Build indices on first run. Call once on app startup."""
        await self._client.build_indices_and_constraints()
        log.info("graphiti.initialized")

    async def remember(
        self,
        fact: str,
        source: str = "gaia_agent",
        entity_type: Optional[str] = None,
        confidence: float = 1.0,
    ) -> dict:
        """
        Write a new fact/observation to the temporal graph.
        Called after every agent learning or external signal.
        """
        episode_name = f"gaia_{entity_type or 'observation'}_{source}"
        source_description = f"entity_type={entity_type or 'unknown'} | confidence={confidence}"

        result = await self._client.add_episode(
            name=episode_name,
            episode_body=fact,
            source=EpisodeType.text,
            source_description=source_description,
        )
        log.info("graphiti.remembered", fact=fact[:80], entity_type=entity_type)
        return {"status": "ok", "episode_id": str(result.episode.uuid) if result.episode else None}

    async def search(self, query: str, num_results: int = 8) -> list[dict]:
        """
        Semantic search over the temporal graph.
        Returns relevant edges/facts for agent context injection.
        """
        results = await self._client.search(query=query, num_results=num_results)
        facts = []
        for edge in results:
            facts.append({
                "fact": edge.fact if hasattr(edge, "fact") else str(edge),
                "source": getattr(edge, "source_description", ""),
                "valid_at": str(getattr(edge, "valid_at", "")),
            })
        log.info("graphiti.searched", query=query[:60], results=len(facts))
        return facts

    async def get_nodes_for_ui(self) -> list[dict]:
        """
        Returns all edges in a format the Context Graph UI can render.
        Each item has: id, source, target, relation.
        """
        # Graphiti search with broad query to pull all recent facts
        results = await self._client.search(query="growth company ICP campaign competitor", num_results=20)
        nodes = []
        for i, edge in enumerate(results):
            nodes.append({
                "id": f"n{i}",
                "source": getattr(edge, "source_node_name", f"Node {i}"),
                "target": getattr(edge, "target_node_name", f"Node {i+1}"),
                "relation": getattr(edge, "name", "RELATES_TO"),
            })
        return nodes

    async def add_competitor_signal(self, competitor: str, signal_type: str, detail: str):
        """Specialized method for writing competitor intelligence to memory."""
        fact = f"Competitor '{competitor}' signal detected: [{signal_type}] — {detail}"
        return await self.remember(fact, source="intelligence_engine", entity_type="Competitor", confidence=0.9)

    async def add_experiment_result(self, hypothesis: str, result: str, winner: str):
        """Record experiment outcomes so they are never repeated if they failed."""
        fact = f"Experiment concluded: '{hypothesis}' — Result: {result} — Winner: {winner}"
        return await self.remember(fact, source="experiment_engine", entity_type="Experiment")

    async def add_published_content(self, title: str, channel: str, url: str):
        """Record all published content for deduplication and repurposing tracking."""
        fact = f"Content published: '{title}' on {channel} — URL: {url}"
        return await self.remember(fact, source="content_engine", entity_type="Content")
