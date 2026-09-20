---
name: marketing-ops
description: The operational brain connecting strategy to execution
---

# Marketing Ops

Connects strategy, campaigns, content, lead generation, CRM, outreach, and analytics.

## Execution Routing
This skill acts as the bridge to the existing n8n automation infrastructure in the `workflows/` directory.
When executing a campaign or operation, it should format the payload and trigger the relevant n8n webhook defined in:
- `workflows/core_intelligence/GrowthAgent_COO_Monitor_Agent.json`
- `workflows/core_intelligence/GrowthAgent_Opportunity_Qualifier.json`
- `workflows/B2B_Lead_Ingestion.json`
- `workflows/B2B_Executive_Outreach.json`
