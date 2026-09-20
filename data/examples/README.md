# Module 08 — AI Knowledge Base Specification

This module serves as the programmatic "brain" of the CloudPulse Growth Engineering OS. Instead of utilizing hardcoded instructions inside prompts, AI writing agents (Claude, Lovable, Gemini, GPT) query these structured JSON files to build emails, draft posts, check sales objections, and format technical descriptions.

## 1. Knowledge Base Directory Map

All files in this folder are formatted in structured JSON for API and agent compatibility:

- [Product_Guides.json](./08-AI-Knowledge-Base/Product_Guides.json): Technical spec, CPT code limits, and 90-day thesis details for Health, Synthetix AI, and Studio.
- [ICP_Definitions.json](./08-AI-Knowledge-Base/ICP_Definitions.json): Target user profiles (Dave, Sam, Fiona) containing pain points, triggers, and values.
- [Brand_Voice_Rules.json](./08-AI-Knowledge-Base/Brand_Voice_Rules.json): Lexicon definitions, approved terms, formatting regulations, and voice filters.
- [Competitor_Intel.json](./08-AI-Knowledge-Base/Competitor_Intel.json): Feature parity comparisons, price limits, and competitor displacement briefs.

## 2. Programmatic Query Map

```
                ┌───────────────────────────────────┐
                │   n8n Content Generation Trigger  │
                └─────────────────┬─────────────────┘
                                  │
                                  ▼
                ┌───────────────────────────────────┐
                │ Query AI Knowledge Base (JSONs)   │
                └─────────────────┬─────────────────┘
                                  │
                                  ▼
                ┌───────────────────────────────────┐
                │ Generate Output in Brand Voice    │
                └───────────────────────────────────┘
```
