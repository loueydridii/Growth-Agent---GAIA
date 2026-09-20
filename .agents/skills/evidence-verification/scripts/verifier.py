import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class EvidenceClaim:
    claim: str
    source: str
    source_date: str
    evidence_text: str
    confidence: float
    status: str  # "VERIFIED", "UNVERIFIED", "REJECTED"

class EvidenceEngine:
    def __init__(self):
        self.claims: List[EvidenceClaim] = []

    def verify_claim(self, claim: str, source: str, source_date: str, evidence_text: str) -> EvidenceClaim:
        """
        Takes a raw claim and checks it against evidence rules.
        In a real implementation, this might call out to the web or a cross-reference model.
        """
        print(f"Analyzing claim: {claim}")
        
        # Simple heuristic scoring for demonstration
        confidence = 1.0
        status = "VERIFIED"
        
        if not source or source == "system":
            confidence -= 0.5
            
        if "competitor" in claim.lower() and not evidence_text:
            confidence -= 0.4
            
        if confidence < 0.6:
            status = "UNVERIFIED"
        if confidence < 0.3:
            status = "REJECTED"
            
        result = EvidenceClaim(
            claim=claim,
            source=source,
            source_date=source_date,
            evidence_text=evidence_text,
            confidence=round(confidence, 2),
            status=status
        )
        
        self.claims.append(result)
        return result
        
    def export_report(self) -> str:
        return json.dumps([c.__dict__ for c in self.claims], indent=2)

if __name__ == "__main__":
    import sys
    engine = EvidenceEngine()
    
    # Simple CLI for the agent to use
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        # Usage: python verifier.py verify "Claim text" "Source URL" "2023-10-01" "Quote from source"
        try:
            claim = sys.argv[2]
            source = sys.argv[3]
            date = sys.argv[4]
            evidence = sys.argv[5]
            
            res = engine.verify_claim(claim, source, date, evidence)
            print(f"Result: [{res.status}] Confidence: {res.confidence}")
            if res.status != "VERIFIED":
                print("WARNING: Claim did not pass strict verification.")
                sys.exit(1)
            sys.exit(0)
        except IndexError:
            print("Usage: python verifier.py verify <claim> <source> <date> <evidence>")
            sys.exit(1)
