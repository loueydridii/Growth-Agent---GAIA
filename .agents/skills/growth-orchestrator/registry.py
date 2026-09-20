from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List

class AutonomyLevel(Enum):
    AUTO = "AUTO"
    APPROVAL = "APPROVAL"
    BLOCKED = "BLOCKED"

@dataclass
class ToolContract:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    autonomy: AutonomyLevel
    risk_level: str
    dependencies: List[str]

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolContract] = {}

    def register(self, tool: ToolContract):
        self.tools[tool.name] = tool
        print(f"Registered Tool: {tool.name} with Autonomy Level: {tool.autonomy.value}")

    def get_tool(self, name: str) -> ToolContract:
        return self.tools.get(name)

    def can_execute(self, name: str) -> bool:
        """Returns True if the tool can be executed automatically, False if human approval is needed."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found in registry.")
        
        if tool.autonomy == AutonomyLevel.BLOCKED:
            raise PermissionError(f"Execution of {name} is globally BLOCKED by policy.")
            
        return tool.autonomy == AutonomyLevel.AUTO
        
    def log_decision(self, goal: str, tool_name: str, rationale: str, memory_retrieved: str, constraints: str):
        """
        Explainability Layer: Logs why the agent made a specific decision.
        Must be called before execution.
        """
        log_entry = {
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            "goal": goal,
            "selected_tool": tool_name,
            "rationale": rationale,
            "memory_context": memory_retrieved,
            "constraints_applied": constraints
        }
        
        with open("decision_audit.log", "a") as f:
            f.write(__import__('json').dumps(log_entry) + "\n")
        
        print(f"Decision logged: {rationale}")
        
    def execute_tool(self, name: str, args: dict, dry_run: bool = False):
        """
        Executes the tool or simulates it if dry_run is True.
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found in registry.")
            
        if dry_run:
            print(f"[DRY-RUN] Simulation Mode Active")
            print(f"[DRY-RUN] Planned Action: Execute '{name}'")
            print(f"[DRY-RUN] Arguments: {args}")
            print(f"[DRY-RUN] Risk Level: {tool.risk_level}")
            print(f"[DRY-RUN] Dependencies Affected: {tool.dependencies}")
            print(f"[DRY-RUN] Action skipped. No side effects occurred.")
            return {"status": "simulated", "estimated_cost": 0.05}
            
        if not self.can_execute(name):
            raise PermissionError(f"Cannot execute '{name}'. Manual APPROVAL required.")
            
        print(f"Executing '{name}' with args: {args}")
        # In production, this dispatches to n8n or an MCP server
        return {"status": "success", "result": "mock_result"}

# Pre-configured Growth Tools
registry = ToolRegistry()

# 1. Safe Analytics (AUTO)
registry.register(ToolContract(
    name="analyze_seo",
    description="Analyze SEO performance and extract insights.",
    input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
    output_schema={"type": "object", "properties": {"score": {"type": "number"}}},
    autonomy=AutonomyLevel.AUTO,
    risk_level="Low",
    dependencies=["seo_api"]
))

# 2. CRM Modification (AUTO)
registry.register(ToolContract(
    name="create_crm_lead",
    description="Create a new lead in the CRM.",
    input_schema={"type": "object", "properties": {"email": {"type": "string"}, "name": {"type": "string"}}},
    output_schema={"type": "object", "properties": {"lead_id": {"type": "string"}}},
    autonomy=AutonomyLevel.AUTO,
    risk_level="Medium",
    dependencies=["crm_api"]
))

# 3. Public Communication (APPROVAL)
registry.register(ToolContract(
    name="publish_post",
    description="Publish a post to social media.",
    input_schema={"type": "object", "properties": {"content": {"type": "string"}, "channel": {"type": "string"}}},
    output_schema={"type": "object", "properties": {"post_id": {"type": "string"}}},
    autonomy=AutonomyLevel.APPROVAL,
    risk_level="High",
    dependencies=["social_api"]
))

# 4. Destructive Action (BLOCKED)
registry.register(ToolContract(
    name="delete_crm_data",
    description="Delete a batch of records from the CRM.",
    input_schema={"type": "object", "properties": {"lead_ids": {"type": "array"}}},
    output_schema={"type": "object", "properties": {"success": {"type": "boolean"}}},
    autonomy=AutonomyLevel.BLOCKED,
    risk_level="Critical",
    dependencies=["crm_api"]
))

if __name__ == "__main__":
    print(f"\nTotal tools registered: {len(registry.tools)}")
    
    # Example execution check
    test_tool = "publish_post"
    try:
        if registry.can_execute(test_tool):
            print(f"Agent can execute {test_tool} autonomously.")
        else:
            print(f"Agent MUST request APPROVAL to execute {test_tool}.")
    except Exception as e:
        print(f"Error: {e}")
