---
name: evidence-verification
description: Verifies generated claims against sources before publication
---

# Evidence Verification

Ensures factual claims are verified against sources. Every factual claim should carry source, date, evidence, and confidence.

## Usage
Before publishing or acting on factual information, you MUST use the verification script:
```bash
python .agents/skills/evidence-verification/scripts/verifier.py verify "Claim text" "Source URL" "Date" "Quote from source"
```

## Rules
- The agent should say "unknown" rather than inventing an answer.
- If the verifier script returns `[REJECTED]` or `[UNVERIFIED]`, the agent MUST NOT act on the information. It must pause and attempt to find a better source or alert the user.
- This covers competitor data, market statistics, SEO claims, and lead intelligence.
