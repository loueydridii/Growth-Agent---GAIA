import json
from dataclasses import dataclass
import datetime

@dataclass
class Experiment:
    id: str
    hypothesis: str
    metric: str
    variants: list
    status: str
    learnings: str = ""

class ExperimentEngine:
    def __init__(self):
        self.experiments = []
        
    def formulate_hypothesis(self, problem: str, proposed_solution: str, metric: str) -> Experiment:
        exp_id = f"EXP-{int(datetime.datetime.now().timestamp())}"
        hypothesis = f"If we {proposed_solution}, then we will improve {metric} because it addresses {problem}."
        
        exp = Experiment(
            id=exp_id,
            hypothesis=hypothesis,
            metric=metric,
            variants=["A (Control)", "B (Treatment)"],
            status="DRAFT"
        )
        self.experiments.append(exp)
        print(f"Created Hypothesis {exp_id}: {hypothesis}")
        return exp
        
    def record_outcome(self, exp_id: str, success: bool, learnings: str):
        """
        Records the outcome of an experiment.
        Crucially, this data MUST be saved to Graphiti memory to ensure 
        the agent does not repeat failed experiments.
        """
        for exp in self.experiments:
            if exp.id == exp_id:
                exp.status = "SUCCESS" if success else "FAILED"
                exp.learnings = learnings
                print(f"Experiment {exp_id} concluded as {exp.status}.")
                print(f"Learnings to push to Graphiti: {learnings}")
                return
        print(f"Experiment {exp_id} not found.")

if __name__ == "__main__":
    import sys
    engine = ExperimentEngine()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "create":
            problem = sys.argv[2]
            solution = sys.argv[3]
            metric = sys.argv[4]
            engine.formulate_hypothesis(problem, solution, metric)
        elif action == "record":
            exp_id = sys.argv[2]
            success = sys.argv[3].lower() == "true"
            learnings = sys.argv[4]
            # Dummy load for state
            engine.experiments.append(Experiment(exp_id, "", "", [], "RUNNING"))
            engine.record_outcome(exp_id, success, learnings)
