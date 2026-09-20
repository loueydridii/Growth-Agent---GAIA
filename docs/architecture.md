# System Architecture

## Overview

Growth-Agent follows a modular, decoupled architecture where reasoning, memory, execution, and data storage are independent systems that communicate via well-defined schemas.

## Core Components

1. **Memory Layer (Postgres)**: The single source of truth. Stores long-term memory (ICP definitions, brand voice), short-term state (in-progress drafts, active leads), and episodic memory (past performance metrics, feedback).
2. **Orchestration Layer (n8n)**: Acts as the nervous system. Routes data between the memory layer, LLM providers, and external APIs (CRM, Email, Social).
3. **Agentic Layer (LLMs)**: The "brains" divided into sub-agents (Scout, Qualifier, Strategist, Writer, Guardian). They receive state from the memory layer via the orchestrator, reason over it, and output structured JSON decisions.
4. **Integration Layer**: API connectors for external platforms. Designed to fail gracefully if an integration goes offline.

## System Flow

```text
External Triggers (Schedule / Webhook / Scraping)
       │
       ▼
Orchestration Engine (Starts Workflow)
       │
       ├── Fetch Context (Memory Layer)
       │
       ▼
LLM Reasoning (Agent Layer)
       │
       ├── Process Context + Input
       ├── Output Structured Decision (JSON)
       │
       ▼
Orchestration Engine (Routes Decision)
       │
       ├── Execute Action (Integration Layer)
       ├── Update State (Memory Layer)
       │
       ▼
Completion / Loop Reset
```
