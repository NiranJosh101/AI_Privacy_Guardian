import asyncio
import json
from typing import Dict, List, Any
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

async def extraction_node(state: ExplorerState) -> Dict[str, Any]:
    regulatory_map = state.get("regulatory_map", {})
    urls_to_scrape = set()
    
    # Extract URLs from the dictionary structure
    for links in regulatory_map.values():
        for link_item in links:
            # Handle both list of strings (from LLM) or list of dicts (from Discovery)
            url = link_item["url"] if isinstance(link_item, dict) else link_item
            if url:
                urls_to_scrape.add(url)

    if not urls_to_scrape:
        print("--- DEBUG: No URLs to extract. Skipping to Aggregation. ---")
        return {"content_store": {}}

    client = MCPClient()
    
    async def scrape_task(url: str) -> tuple[str, str]:
        try:
            # Note: Ensure your MCP server has the 'extract_policy_content' tool!
            response = await client.call_tool("extract_policy_content", {"url": url})
            
            # --- THE FIX: Peel the Content Onion ---
            content_list = getattr(response, 'content', [])
            
            if content_list and len(content_list) > 0:
                # Grab the first block specifically
                first_item = content_list 
                
                # Get the text string
                if hasattr(first_item, 'text'):
                    return (url, first_item.text)
                return (url, str(first_item))
            
            return (url, f"Empty content returned for {url}")
        except Exception as e:
            return (url, f"Error extracting {url}: {str(e)}")

    try:
        await client.connect()
        print(f"--- DEBUG: Extracting {len(urls_to_scrape)} URLs in parallel ---")
        
        # Gather all tasks concurrently
        results = await asyncio.gather(*(scrape_task(u) for u in urls_to_scrape))
        
        # Create the update map
        extracted_data = {url: text for url, text in results}
        
        return {
            "content_store": extracted_data, # LangGraph merges this into state
            "is_blocked": False
        }

    except Exception as e:
        print(f"--- DEBUG: Extraction Node CRASHED: {str(e)} ---")
        return {"error_log": [f"Extraction batch failed: {str(e)}"]}
    finally:
        try:
            await client.disconnect()
        except:
            pass