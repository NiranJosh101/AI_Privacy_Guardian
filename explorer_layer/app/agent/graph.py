from langgraph.graph import StateGraph, END
from app.agent.state import ExplorerState
from app.agent.node.validation import validation_node
from app.agent.node.discovery import discovery_node
from app.agent.node.classification import classification_node
from app.agent.node.extraction import extraction_node
from app.agent.node.aggregation import aggregation_node

# Define the Routing Logic
def should_continue(state: ExplorerState):
    
    is_blocked = state.get("is_blocked", False)
    print(f"--- DEBUG: Routing Check | is_blocked: {is_blocked} ---")
    
    if is_blocked:
        print("--- DEBUG: Routing to END ---")
        return "end"
    
    print("--- DEBUG: Routing to DISCOVERY ---")
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