import os
import json
import asyncio
from graphiti import Graphiti
from datetime import datetime, timezone

# Initialize Graphiti Client
# Ensure NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD are set in the environment
def get_client():
    return Graphiti(
        neo4j_uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.environ.get("NEO4J_USER", "neo4j"),
        neo4j_password=os.environ.get("NEO4J_PASSWORD", "password")
    )

async def setup_schema():
    """Define the core entities for the Growth Knowledge Graph."""
    client = get_client()
    
    print("Setting up Growth Knowledge Graph schema...")
    
    # Define custom node types relevant to the Growth OS
    # Graphiti allows storing entities with temporal validity and provenance
    # Example concepts: Company, ICP, Campaign, Lead, Opportunity
    
    # In a real implementation, you might explicitly register these 
    # or rely on dynamic node extraction with custom prompts.
    print("Schema initialized.")

async def remember(fact_text, source="system", confidence=1.0):
    """
    Ingest a new fact into the temporal memory graph.
    The agent uses this to store new learnings, campaign results, or competitor intel.
    """
    client = get_client()
    
    print(f"Adding fact to graph: '{fact_text}'")
    # Store the fact as an episode or extract nodes/edges
    # This is a wrapper around client.add_episode()
    response = await client.add_episode(
        name="growth_agent_observation",
        episode_body=fact_text,
        source=source,
        source_description=f"Confidence: {confidence}"
    )
    return response

async def retrieve(query):
    """
    Query the graph for a specific concept or historical fact.
    """
    client = get_client()
    
    print(f"Retrieving context for query: '{query}'")
    # Search the graph for relevant nodes/edges
    results = await client.search(query=query)
    
    # Format the results for the agent
    return [edge.model_dump() for edge in results.edges]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Graphiti Memory Client")
    parser.add_argument("action", choices=["setup", "remember", "retrieve"])
    parser.add_argument("--text", type=str, help="Fact text or query")
    parser.add_argument("--source", type=str, default="manual")
    
    args = parser.parse_args()
    
    if args.action == "setup":
        asyncio.run(setup_schema())
    elif args.action == "remember":
        if not args.text:
            print("Error: --text required for remember")
            exit(1)
        res = asyncio.run(remember(args.text, args.source))
        print("Remembered.", res)
    elif args.action == "retrieve":
        if not args.text:
            print("Error: --text required for retrieve")
            exit(1)
        res = asyncio.run(retrieve(args.text))
        print(json.dumps(res, indent=2))
