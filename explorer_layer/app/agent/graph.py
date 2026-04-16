from langgraph.graph import StateGraph, END
from app.agent.state import ExplorerState
from app.agent.node.validation import validation_node
from app.agent.node.discovery import discovery_node
from app.agent.node.classification import classification_node
from app.agent.node.extraction import extraction_node
from app.agent.node.aggregation import aggregation_node

def should_continue(state: ExplorerState):
    is_blocked = state.get("is_blocked", False)
    status_code = state.get("status_code", 0)
    
    print(f"--- DEBUG: Routing Check | Status: {status_code} | is_blocked: {is_blocked} ---")

    if status_code == 200:
        return "continue"
    
    if is_blocked:
        return "end"
    
    return "continue"

# Build the Graph
workflow = StateGraph(ExplorerState)

# Add nodes
workflow.add_node("validate", validation_node)
workflow.add_node("discovery", discovery_node)
workflow.add_node("classify", classification_node)
workflow.add_node("extract", extraction_node)
workflow.add_node("aggregate", aggregation_node)

# Entry Point
workflow.set_entry_point("validate")

# Conditional Edge from Validate
workflow.add_conditional_edges(
    "validate",
    should_continue,
    {
        "continue": "discovery",
        "end": END
    }
)

# THE FAN-OUT:
# Discovery now has TWO outgoing edges. 
# LangGraph will automatically execute these in parallel.
workflow.add_edge("discovery", "classify")
workflow.add_edge("discovery", "extract")

# THE FAN-IN:
# Both parallel nodes point to 'aggregate'. 
# 'aggregate' will only trigger once both are done.
workflow.add_edge("classify", "aggregate")
workflow.add_edge("extract", "aggregate")

workflow.add_edge("aggregate", END)

# Compile
explorer_agent = workflow.compile()