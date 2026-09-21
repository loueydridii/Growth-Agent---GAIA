"""
backend/db.py — Single source of truth for all database connections.
Loads credentials from .env, never from hardcoded values.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import redis.asyncio as aioredis
from graphiti_core import Graphiti

load_dotenv()


# ── SQLAlchemy (Postgres) ─────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set in .env")
    return url


_engine = None
_SessionFactory = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _get_database_url(),
            echo=False,
            pool_size=10,
            max_overflow=20,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _SessionFactory


async def get_db_session() -> AsyncSession:
    """FastAPI dependency — yields a database session per request."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Redis ─────────────────────────────────────────────────────────────────────

_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = await aioredis.from_url(redis_url, decode_responses=True)
    return _redis_client


# ── Graphiti (Neo4j Temporal Graph) ──────────────────────────────────────────

_graphiti_client = None


def get_graphiti() -> Graphiti:
    global _graphiti_client
    if _graphiti_client is None:
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            raise RuntimeError(
                "NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in .env"
            )

        _graphiti_client = Graphiti(
            neo4j_uri=uri,
            neo4j_user=user,
            neo4j_password=password,
        )
    return _graphiti_client


async def init_db():
    """Create all Postgres tables and Graphiti schema on startup."""
    from backend.models import company  # noqa: ensure models are registered
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Build Graphiti indices on Neo4j
    g = get_graphiti()
    await g.build_indices_and_constraints()
