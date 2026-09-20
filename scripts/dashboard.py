import streamlit as st
import json
import os

st.set_page_config(page_title="Growth OS Executive Dashboard", layout="wide")

st.title("Growth OS Executive Dashboard")
st.markdown("Monitor autonomous Agent decisions, experiments, and pending approvals.")

# Mock Data Loading (In production, this would query Postgres/Graphiti)
def load_audit_log():
    try:
        with open(".agents/skills/growth-orchestrator/decision_audit.log", "r") as f:
            return [json.loads(line) for line in f.readlines()]
    except FileNotFoundError:
        return []

st.header("1. CEO Goal Tracking")
col1, col2, col3 = st.columns(3)
col1.metric("Pipeline Growth (Target: +30%)", "+12%", delta="12%")
col2.metric("Pending Approvals", "2")
col3.metric("Active Experiments", "3")

st.divider()

st.header("2. Decision Audit Trail")
logs = load_audit_log()
if logs:
    for log in reversed(logs[-5:]):  # Show last 5
        with st.expander(f"[{log['timestamp']}] Tool Executed: {log['selected_tool']}"):
            st.write(f"**Goal:** {log['goal']}")
            st.write(f"**Rationale:** {log['rationale']}")
            st.write(f"**Constraints:** {log['constraints_applied']}")
else:
    st.info("No autonomous decisions logged yet.")

st.divider()

st.header("3. Pending Policy Approvals")
st.warning("The Orchestrator requires your approval to execute the following BLOCKED/APPROVAL actions:")
approval_data = [
    {"Tool": "publish_post", "Risk": "High", "Rationale": "Publish Q3 recap on LinkedIn to drive inbound."},
    {"Tool": "delete_crm_data", "Risk": "Critical", "Rationale": "Prune 500 bounced emails from CRM to improve deliverability."}
]
st.table(approval_data)
st.button("Approve Selected Actions", type="primary")

st.divider()

st.header("4. Growth Knowledge Graph")
st.markdown("Visualizing latest nodes stored in **Graphiti Temporal Memory**:")
st.code("""
(Company: ACME) -[TARGETS]-> (ICP: Enterprise DevOps)
(ICP: Enterprise DevOps) -[HAS_PROBLEM]-> (Problem: Slow CI/CD)
(Campaign: Q3 DevOps Push) -[ADDRESSES]-> (Problem: Slow CI/CD)
""")
