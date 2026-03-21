import asyncio
from typing import Dict, List, Any
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

async def extraction_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Parallelized extraction of all identified regulatory documents.
    """
    # 1. Collect all unique URLs from the refined map
    # We use a set to avoid scraping the same URL twice if it's in two categories
    urls_to_scrape = set()
    for category_links in state["regulatory_map"].values():
        for link_data in category_links:
            urls_to_scrape.add(link_data["url"])

    if not urls_to_scrape:
        return {"error_log": ["No URLs found to extract."]}

    client = MCPClient()
    
    async def scrape_task(url: str) -> tuple[str, str]:
        """Helper to run a single tool call and return (url, content)"""
        try:
            # Note: The client handles the stdio communication for each call
            content = await client.call_tool("extract_policy_content", {"url": url})
            return (url, content)
        except Exception as e:
            return (url, f"Failed to extract {url}: {str(e)}")

    try:
        await client.connect()
        
        # 2. Parallel Execution using asyncio.gather
        # This kicks off all scrapers at once!
        tasks = [scrape_task(url) for url in urls_to_scrape]
        results = await asyncio.gather(*tasks)
        
        # 3. Convert results list back into a dictionary for the State
        new_content = {url: content for url, content in results}
        
        return {
            "content_store": new_content,
            "is_blocked": False
        }

    except Exception as e:
        return {"error_log": [f"Extraction batch failed: {str(e)}"]}
    
    finally:
        await client.disconnect()