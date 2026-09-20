---
name: growth-strategy
description: Understands business objectives, funnels, ICPs, and experiment design
---

# Growth Strategy

Provides reasoning for: Goal -> Problem -> Opportunity -> Hypothesis -> Channel -> Action -> Experiment -> Measurement -> Learn.

## Knowledge Base Integration
This skill must ground its reasoning using the business context provided in `data/examples`:
- [ICP Definitions](file:///c:/Users/louey/Desktop/vscode/Growth-Agent/data/examples/ICP_Definitions.json)
- [Product Guides](file:///c:/Users/louey/Desktop/vscode/Growth-Agent/data/examples/Product_Guides.json)
- [Competitor Intel](file:///c:/Users/louey/Desktop/vscode/Growth-Agent/data/examples/Competitor_Intel.json)

Before suggesting any strategy, parse these definitions to ensure the proposed funnel and targeting align with the organization's verified definitions.

## The Autonomous Opportunity Engine
Raw signals (e.g., traffic drops, competitor pricing changes, new leads) are continuously evaluated against active goals.
To evaluate a signal, run the scanner:
```bash
python .agents/skills/growth-strategy/scripts/opportunity_scanner.py scan <source> <type> <description>
```
If the scanner returns `[ACTIONABLE]`, the orchestrator must plan a response.

## The Experiment Engine
Instead of just "generating more content," formulate hypotheses and track them. Do not repeat failed experiments.
**To formulate:**
```bash
python .agents/skills/growth-strategy/scripts/experiment_engine.py create "<problem>" "<solution>" "<metric>"
```
**To record outcome:**
```bash
python .agents/skills/growth-strategy/scripts/experiment_engine.py record "<EXP_ID>" "<true/false>" "<learnings>"
```
Failures must be explicitly recorded so they sync to the Graphiti temporal memory.
