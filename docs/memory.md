# Memory Layer

The memory layer is the foundation of the Growth-Agent. Without it, the LLMs are stateless and amnesiac. By reading and writing to a central Postgres database, the agent maintains context over time.

## Architecture

We use a relational database (Postgres) because growth operations require structured, queryable data (e.g., "Find all LinkedIn posts from last month that scored above 80% engagement").

## Core Schemas

### 1. Knowledge Base (Long-term Memory)
- **`brand_voice`**: Rules, tone guidelines, and banned words.
- **`icp_definitions`**: Target audience profiles, pain points, and desires.
- **`product_context`**: What the organization actually sells or does.

### 2. State & Operations (Short-term Memory)
- **`signals`**: Raw inputs from the outside world.
- **`opportunities`**: Qualified signals waiting for action.
- **`drafts`**: In-progress content or actions waiting for Brand Guardian approval.

### 3. Telemetry (Episodic Memory)
- **`campaign_results`**: Engagement metrics, open rates, click-through rates.
- **`agent_feedback`**: Logs of when the Brand Guardian rejected a draft and why, used for fine-tuning future prompts.

## Memory Injection

Before an agent acts, the orchestrator queries the relevant memory.
For example, before the `Blog_Writer_Agent` drafts an article about "AI in Healthcare", the orchestrator injects:
1. The ICP definition for Healthcare CTOs.
2. The Brand Voice rules.
3. The 3 best-performing past blog posts on similar topics (retrieved via vector similarity or tags).
