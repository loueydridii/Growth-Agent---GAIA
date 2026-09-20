---
name: growth-orchestrator
description: Master router deciding which specialist/agent/workflow to invoke
---

# Growth Orchestrator

This skill is the central router of the Growth-Agent. It receives the high-level goals and determines the appropriate specialist skills, workflows, or agents to invoke.

## Capabilities
- Routing tasks based on intent.
- Orchestrating cross-skill workflows.

## Master Routing Logic
When a request is received, use the following logic to delegate to the appropriate sub-skill:
1. **Planning & Decisions**: If the request is complex, route to `agent-planner` and use the `decision-engine` for critical path choices.
2. **Context & Memory**: Always query `context-engine` and `graphiti-memory` before executing a workflow to ensure temporal facts and state are accurate.
3. **Strategy & Ops**: For campaign execution or content strategy, invoke `growth-strategy` to define the parameters, then pass execution to `marketing-ops`.
4. **Verification**: Route any generated content or factual claims through `evidence-verification` before finalizing.
5. **Observability**: Ensure all steps emit traces that can be logged by `agent-observability`.
