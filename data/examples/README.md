# GAIA — Knowledge Base Specification

This directory serves as the structured knowledge repository for the GAIA Growth OS. Instead of hardcoding product claims, competitors, or tone instructions inside prompts, GAIA's autonomous agents query these modular JSON files to synthesize outbound outreach, evaluate trends, score signals, and draft multichannel content.

## 1. Directory Structure

Each company customizes these JSON files to match their own commercial stack:

- [Product_Guides.json](./Product_Guides.json): Core technologies, value propositions, pricing tiers, and quantifiable pitch anchors across product lines.
- [ICP_Definitions.json](./ICP_Definitions.json): Granular target buyer personas including seniority, firmographics, pain points, and forbidden topics.
- [Brand_Voice_Rules.json](./Brand_Voice_Rules.json): Tone anchors, forbidden phrases, approved vocabulary substitutes, and length regulations per channel.
- [Competitor_Intel.json](./Competitor_Intel.json): Market rivals, structural strengths, weaknesses, and targeted displacement arguments.

## 2. Dynamic Context Injection Architecture

```
┌──────────────────────────────────────────────┐
│  Agent Trigger (Scheduler / Signal Detection)│
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Query Knowledge Base & Vector Memory (JSON) │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Generate Personalized Output in Brand Voice │
└──────────────────────────────────────────────┘
```
