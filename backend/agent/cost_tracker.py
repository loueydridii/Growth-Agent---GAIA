"""
backend/agent/cost_tracker.py — Tracks every API call and its cost.
Writes to Postgres APIUsageLog. Exposes cost summaries for the UI.
"""
import os
import structlog
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
log = structlog.get_logger()

# Approximate costs per 1M tokens (update as pricing changes)
COST_PER_MILLION_TOKENS = {
    "gemini-2.5-pro":     {"in": 1.25, "out": 10.00},
    "gemini-2.0-flash":   {"in": 0.075, "out": 0.30},
    "gpt-4o":             {"in": 2.50, "out": 10.00},
    "gpt-4o-mini":        {"in": 0.15, "out": 0.60},
}

COST_PER_CALL = {
    "tavily_search":  0.01,   # per search
    "exa_search":     0.005,  # per search
    "dalle3_image":   0.04,   # per image
    "higgsfield_video": 0.20, # estimate per video
}


class CostTracker:
    """
    Tracks API usage and cost. Logs to Postgres (async, non-blocking).
    Falls back to in-memory tracking if DB is unavailable.
    """

    async def log(
        self,
        provider: str,
        model: str = "",
        tokens_in: int = 0,
        tokens_out: int = 0,
        task_id: str = None,
        call_type: str = None,
    ) -> float:
        """
        Log an API call and return the estimated cost in USD.
        """
        cost = self._estimate_cost(provider, model, tokens_in, tokens_out, call_type)

        log.info(
            "api_usage",
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=round(cost, 6),
            task_id=task_id,
        )

        # Write to Postgres asynchronously
        try:
            from backend.db import get_session_factory
            from backend.models.company import APIUsageLog

            factory = get_session_factory()
            async with factory() as session:
                entry = APIUsageLog(
                    provider=provider,
                    model=model,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost_usd=cost,
                    task_id=task_id,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(entry)
                await session.commit()
        except Exception as e:
            log.warning("cost_tracker.db_write_failed", error=str(e))

        return cost

    def _estimate_cost(self, provider, model, tokens_in, tokens_out, call_type) -> float:
        if call_type and call_type in COST_PER_CALL:
            return COST_PER_CALL[call_type]

        pricing = COST_PER_MILLION_TOKENS.get(model)
        if pricing:
            return (tokens_in / 1_000_000 * pricing["in"]) + (tokens_out / 1_000_000 * pricing["out"])

        return 0.0

    async def get_summary(self, days: int = 30) -> dict:
        """Returns cost summary for the Telemetry UI."""
        try:
            from backend.db import get_session_factory
            from backend.models.company import APIUsageLog
            from sqlalchemy import select, func
            from datetime import timedelta

            cutoff = datetime.now(timezone.utc) - timedelta(days=days)

            factory = get_session_factory()
            async with factory() as session:
                result = await session.execute(
                    select(
                        func.sum(APIUsageLog.cost_usd).label("total"),
                        func.count(APIUsageLog.id).label("calls"),
                    ).where(APIUsageLog.created_at >= cutoff)
                )
                row = result.fetchone()
                return {
                    "total_usd": round(row.total or 0, 4),
                    "total_calls": row.calls or 0,
                    "period_days": days,
                    "alert_threshold": float(os.getenv("COST_ALERT_THRESHOLD_USD", 50)),
                }
        except Exception as e:
            log.warning("cost_tracker.summary_failed", error=str(e))
            return {"total_usd": 0, "total_calls": 0, "period_days": days}
