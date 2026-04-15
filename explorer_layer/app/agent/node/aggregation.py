from typing import Dict, Any
from langsmith import traceable
from app.agent.state import ExplorerState


@traceable(name="Aggregation Node", run_type="chain")
def aggregation_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Stitches multiple documents into one structured report 
    with clear source markers and prints the final result.
    """
    content_store = state.get("content_store", {})
    regulatory_map = state.get("regulatory_map", {})
    base_url = state.get("base_url", "Unknown Domain")
    
    if not content_store:
        error_msg = "# Error\nNo content was successfully extracted."
        print(f"\n--- AGGREGATION FAILED: {base_url} ---\n{error_msg}")
        return {"final_report": error_msg}

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
                report_sections.append(content)
                report_sections.append("\n---\n") 
            else:
                report_sections.append(f"### Source: {url} (Extraction Failed or No Content)")

    final_markdown = "\n".join(report_sections)

    # --- ADDED PRINT FOR VISIBILITY ---
    print("\n" + "="*50)
    print(f" FINAL AGGREGATED REPORT FOR: {base_url}")
    print(f" TOTAL CHARACTERS: {len(final_markdown)}")
    print("="*50)
    print(final_markdown)  # This prints the full Markdown to your console
    print("="*50 + "\n")
    
    print(f"--- AGGREGATION COMPLETE: Report generated for {base_url} ---")
    
    return {
        "final_report": final_markdown,
        "is_blocked": False 
    }