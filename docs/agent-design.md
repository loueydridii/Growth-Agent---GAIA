# Agent Design & Decision Engine

## Multi-Agent Paradigm

Instead of a single monolithic prompt, Growth-Agent uses a swarm of specialized sub-agents. Each agent has a single responsibility, a specific set of tools, and a distinct persona.

### 1. Intelligence Scouts
- **Role**: Monitor external sources (RSS feeds, competitor sites, social media).
- **Output**: Raw "Signals" (JSON).

### 2. The Qualifier
- **Role**: Triage signals based on the organization's ICP and current objectives.
- **Decision Matrix**:
  - `reject`: Irrelevant to current goals.
  - `archive`: Relevant, but not a priority.
  - `action`: High value opportunity. Output as "Opportunity" (JSON).

### 3. The Strategist
- **Role**: Determine the best medium (blog, LinkedIn, email) and angle for an Opportunity.
- **Context Required**: Current content calendar, active A/B tests, past performance of similar angles.

### 4. Content Writers (Specialized)
- **Role**: Draft the actual content. Separate agents exist for LinkedIn, SEO Blogs, and Newsletters to maintain platform-specific formatting and tone.

### 5. The Brand Guardian
- **Role**: Quality assurance. 
- **Action**: Critiques the Writer's output against the `Brand_Voice_Rules.json`. If it fails, it provides a feedback loop to the Writer to retry. If it passes, it approves the draft for human review or autonomous publishing.

## Decision Schema

All agents communicate using structured JSON. A standard decision object looks like this:

```json
{
  "agent_id": "qualifier_01",
  "input_signal_id": "sig_12345",
  "reasoning": "The signal mentions a new technology highly relevant to our ICP's pain points. It aligns with our Q3 goal of establishing thought leadership in AI.",
  "decision": "action",
  "priority_score": 85,
  "recommended_next_step": "Draft a LinkedIn thought-leadership post."
}
```
