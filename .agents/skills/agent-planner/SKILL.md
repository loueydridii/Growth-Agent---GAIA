---
name: agent-planner
description: Breaks growth objectives into executable plans and dependencies
---

# Agent Planner

This skill takes high-level growth objectives and breaks them down into actionable steps, identifying dependencies and required resources.

## The Planner → Executor → Critic Loop (PEC)

The planner does not just generate a list of steps and walk away. It must participate in the self-healing execution cycle:

1. **Plan**: Generate the step-by-step dependency graph.
2. **Execute Delegation**: The orchestrator sends the step to the Executor (e.g., `marketing-ops` or a specific n8n webhook).
3. **Critic Inspection**: Once the executor finishes (or fails), the output MUST be routed back here to the Critic.
4. **Evaluate & Self-Heal**:
   - *Success*: Move to the next planned step.
   - *Failure (API timeout, missing data, malformed output)*: The Critic must diagnose the failure, update the active plan with a retry strategy or fallback tool, and resubmit.
   - *Escalation*: If the step fails 3 times, the Critic must mark the plan as BLOCKED and escalate to the user.

Do not allow "silent failures" where a step fails and the system ignores it.
