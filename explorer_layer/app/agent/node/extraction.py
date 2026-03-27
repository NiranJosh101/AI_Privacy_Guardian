import asyncio
import json
from typing import Dict, List, Any
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

async def extraction_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Parallelized extraction of all identified regulatory documents.
    """
    # 1. Collect all unique URLs from the refined map
    # This now works because Discovery Node returns a Dict!
    urls_to_scrape = set()
    regulatory_map = state.get("regulatory_map", {})
    
    for category_links in regulatory_map.values():
        for link_data in category_links:
            if isinstance(link_data, dict) and "url" in link_data:
                urls_to_scrape.add(link_data["url"])

    if not urls_to_scrape:
        return {"error_log": ["No URLs found to extract."]}

    client = MCPClient()
    
    async def scrape_task(url: str) -> tuple[str, str]:
        """Helper to run a single tool call and return (url, content_text)"""
        try:
            response = await client.call_tool("extract_policy_content", {"url": url})
            
            # ✅ PEEL THE ONION: Get the actual text from the MCP response
            content_list = getattr(response, 'content', response)
            if content_list and isinstance(content_list, list) and len(content_list) > 0:
                first_item = content_list
                content_text = first_item.text if hasattr(first_item, 'text') else str(first_item)
                return (url, content_text)
            
            return (url, "No content found in MCP response")
        except Exception as e:
            return (url, f"Failed to extract {url}: {str(e)}")

    try:
        await client.connect()
        
        # 2. Parallel Execution
        print(f"--- DEBUG: Extracting {len(urls_to_scrape)} URLs in parallel ---")
        tasks = [scrape_task(url) for url in urls_to_scrape]
        results = await asyncio.gather(*tasks)
        
        # 3. Convert results list back into a dictionary
        # new_content now maps URL -> Actual String Content
        new_content = {url: content for url, content in results}
        
        return {
            "content_store": new_content,
            "is_blocked": False
        }

    except Exception as e:
        print(f"--- DEBUG: Extraction Node CRASHED: {str(e)} ---")
        return {"error_log": [f"Extraction batch failed: {str(e)}"]}
    
    finally:
        await client.disconnect()