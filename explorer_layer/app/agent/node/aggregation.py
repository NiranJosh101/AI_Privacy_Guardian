from typing import Dict, Any
from app.agent.state import ExplorerState

def aggregation_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Stitches multiple documents into one structured report 
    with clear source markers.
    """
    content_store = state.get("content_store", {})
    regulatory_map = state.get("regulatory_map", {})
    base_url = state.get("base_url", "Unknown Domain")
    
    if not content_store:
        return {"final_report": "# Error\nNo content was successfully extracted."}

    report_sections = [f"# Regulatory Suite for {base_url}\n"]
    report_sections.append("This document aggregates all discovered legal and privacy information.\n")

    for category, links in regulatory_map.items():
        report_sections.append(f"## CATEGORY: {category.upper()}")
        
        for link_data in links:
            # --- ROBUST URL EXTRACTION ---
            # Handles both {"url": "..."} (Discovery) and "https://..." (LLM Refined)
            url = link_data["url"] if isinstance(link_data, dict) else link_data
            
            content = content_store.get(url)
            
            if content:
                report_sections.append(f"### Source: {url}")
                # Optional: Add a small snippet or the full content
                report_sections.append(content)
                report_sections.append("\n---\n") 
            else:
                report_sections.append(f"### Source: {url} (Extraction Failed or No Content)")

    final_markdown = "\n".join(report_sections)

    print(f"--- AGGREGATION COMPLETE: Report generated for {base_url} ---")
    
    return {
        "final_report": final_markdown,
        "is_blocked": False # Ensure we don't accidentally stop the graph here
    }