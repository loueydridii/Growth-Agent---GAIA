# Automation & Orchestration

Growth-Agent uses **n8n** as its orchestration layer. The n8n workflows act as the central nervous system, connecting the LLM agents, the Postgres database, and external APIs.

## Why n8n?

1. **Visual State Machine**: It allows developers and operators to visually track the execution path of the agent.
2. **Error Handling**: Built-in retry logic and error catching for API failures.
3. **Decoupling**: The business logic (LLM prompts) is separated from the infrastructure (API connectors).

## Core Workflow Types

### 1. Cron-Triggered Scouts
These workflows run on a schedule (e.g., every 6 hours). They pull data from RSS feeds, web scrapers, or social media APIs, format it, and insert it into the `signals` table in the memory layer.

### 2. Event-Driven Reasoning Loops
These workflows are triggered via webhooks (e.g., when a new signal is inserted into the database). They fetch the signal, inject it into an LLM node (the Qualifier or Strategist), and process the JSON response to update the database state.

### 3. Action Executors
These workflows take an approved "Draft" or "Decision" from the memory layer and execute the final action via external APIs (e.g., POST to LinkedIn, POST to CRM, Send Email).

## Best Practices

- **Atomic Workflows**: Keep workflows small and focused. Use the "Execute Workflow" node to call sub-workflows (e.g., a generic "LLM Reasoning" sub-workflow) rather than building massive, complex webs.
- **Fail Gracefully**: If an API is rate-limited, the workflow should catch the error, update the memory state to `failed_retry`, and exit, allowing a secondary sweeper workflow to retry later.
