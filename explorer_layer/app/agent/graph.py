from langgraph.graph import StateGraph, END
from app.agent.state import ExplorerState
from app.agent.node.validation import validation_node
from app.agent.node.discovery import discovery_node
from app.agent.node.classification import classification_node
from app.agent.node.extraction import extraction_node
from app.agent.node.aggregation import aggregation_node

def should_continue(state: ExplorerState):
    # Pull both flags from the state
    is_blocked = state.get("is_blocked", False)
    status_code = state.get("status_code", 0)
    
    print(f"--- DEBUG: Routing Check | Status: {status_code} | is_blocked: {is_blocked} ---")

    # If we got a 200, we ALWAYS try Discovery. 
    # This ignores the "block_detected" keywords that were failing you before.
    if status_code == 200:
        print("--- DEBUG: Routing to DISCOVERY (Status 200 Override) ---")
        return "continue"
    
    if is_blocked:
        print("--- DEBUG: Hard Block Detected. Routing to END ---")
        return "end"
    
    return "continue"
    
# Build the Graph
workflow = StateGraph(ExplorerState)

# Add our specialized nodes
workflow.add_node("validate", validation_node)
workflow.add_node("discovery", discovery_node)
workflow.add_node("classify", classification_node)
workflow.add_node("extract", extraction_node)
workflow.add_node("aggregate", aggregation_node)

# Define the Edges (The Connections)
workflow.set_entry_point("validate")

# Check health after validation
workflow.add_conditional_edges(
    "validate",
    should_continue,
    {
        "continue": "discovery",
        "end": END
    }
)

# Standard linear flow for the rest
workflow.add_edge("discovery", "classify")
workflow.add_edge("classify", "extract")
workflow.add_edge("extract", "aggregate")
workflow.add_edge("aggregate", END)

# Compile the Graph
# This turns the blueprint into an executable 'Runnable'
explorer_agent = workflow.compile()