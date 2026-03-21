from typing import Dict, Any
from app.agent.state import ExplorerState

def aggregation_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Stitches multiple documents into one structured report 
    with clear source markers.
    """
    content_store = state.get("content_store", {})
    regulatory_map = state.get("regulatory_map", {})
    
    if not content_store:
        return {"final_report": "# Error\nNo content was successfully extracted."}

    # Start building the Master Markdown
    report_sections = [f"# Regulatory Suite for {state['base_url']}\n"]
    report_sections.append("This document aggregates all discovered legal and privacy information.\n")

    # Iterate through our categories to keep the report structured
    for category, links in regulatory_map.items():
        report_sections.append(f"## CATEGORY: {category.upper()}")
        
        for link_data in links:
            url = link_data["url"]
            content = content_store.get(url)
            
            if content:
                report_sections.append(f"### Source: {url}")
                report_sections.append(content)
                report_sections.append("\n---\n") # Separator between docs
            else:
                report_sections.append(f"### Source: {url} (Extraction Failed)")

    # Join everything into the final string
    final_markdown = "\n".join(report_sections)

    return {
        "final_report": final_markdown,
        "current_step": "complete"
    }