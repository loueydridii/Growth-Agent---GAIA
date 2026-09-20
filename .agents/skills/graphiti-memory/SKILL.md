---
name: graphiti-memory
description: Temporal knowledge graph memory for facts, entities, and relationships
---

# Graphiti Memory

Manages the ingestion, retrieval, update, and consolidation of facts using a temporal knowledge graph (Graphiti).

## Operations
The memory logic is encapsulated in `scripts/client.py`. Use it to interact with the temporal graph.

**Setup Schema:**
```bash
python .agents/skills/graphiti-memory/scripts/client.py setup
```

**Ingest a Fact:**
```bash
python .agents/skills/graphiti-memory/scripts/client.py remember --text "Competitor X launched a new AI feature on Oct 1st." --source "web_scout"
```

**Retrieve Context:**
```bash
python .agents/skills/graphiti-memory/scripts/client.py retrieve --text "What features did Competitor X launch recently?"
```

## Evidence & Truth Rules
- Never hallucinate relationships. If the graph does not return a fact, do not invent one.
- Always include the `--source` when remembering a fact.
- Only pass verified claims to the execution layer.
