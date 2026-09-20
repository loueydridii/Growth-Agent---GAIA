import json
from dataclasses import dataclass
from typing import List

@dataclass
class Opportunity:
    source: str
    signal_type: str
    description: str
    estimated_impact: float
    confidence: float
    status: str

class OpportunityEngine:
    def __init__(self):
        self.active_goals = []
        
    def load_goals(self, goals: List[dict]):
        self.active_goals = goals
        print(f"Loaded {len(goals)} active business goals.")
        
    def score_signal(self, source: str, signal_type: str, description: str) -> Opportunity:
        """
        Evaluates a raw signal (e.g. competitor pricing change, traffic drop)
        against the active business goals to determine if it is an actionable opportunity.
        """
        # Placeholder scoring logic
        impact = 0.5
        confidence = 0.7
        
        if signal_type == "competitor_change":
            impact = 0.8
            
        if "lead" in description.lower() or "pipeline" in description.lower():
            impact = 0.9
            
        score = impact * confidence
        
        status = "PENDING_REVIEW"
        if score > 0.6:
            status = "ACTIONABLE"
        elif score < 0.3:
            status = "IGNORED"
            
        opp = Opportunity(
            source=source,
            signal_type=signal_type,
            description=description,
            estimated_impact=impact,
            confidence=confidence,
            status=status
        )
        print(f"Scored Signal: [{status}] Impact: {impact}, Confidence: {confidence}")
        return opp

if __name__ == "__main__":
    import sys
    engine = OpportunityEngine()
    engine.load_goals([{"metric": "pipeline", "target": "+30%"}])
    
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        source = sys.argv[2]
        signal_type = sys.argv[3]
        desc = sys.argv[4]
        engine.score_signal(source, signal_type, desc)
