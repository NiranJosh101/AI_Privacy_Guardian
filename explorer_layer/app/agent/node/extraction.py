import asyncio
import json
from typing import Dict, Any
from langsmith import traceable
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

@traceable(name="Extraction Node", run_type="chain")
async def extraction_node(state: ExplorerState) -> Dict[str, Any]:
    regulatory_map = state.get("regulatory_map", {})
    urls_to_scrape = set()

    # Extract URLs from the state
    for links in regulatory_map.values():
        for link_item in links:
            url = link_item["url"] if isinstance(link_item, dict) else link_item
            if url:
                urls_to_scrape.add(url)

    if not urls_to_scrape:
        print("--- DEBUG: No URLs to extract. Skipping to Aggregation. ---")
        return {"content_store": {}}

    client = MCPClient()

    async def scrape_task(url: str) -> tuple[str, str]:
        try:
            print(f"\n [CALLING MCP TOOL] {url}")

            response = await client.call_tool(
                "extract_policy_content",
                {"url": url}
            )

            # MCP tools return a list of content items (usually TextContent)
            content_list = getattr(response, "content", [])

            if not content_list:
                print(f"❌ [EMPTY MCP RESPONSE] {url}")
                return (url, f"Empty content returned for {url}")

            # Get the first item from the response
            first_item = content_list
            
            # Extract the string content. 
            # Because the tool now returns a Dict, the MCP SDK typically 
            # puts the string representation of that dict in the .text field.
            raw_output = first_item.text if hasattr(first_item, "text") else str(first_item)

            # --- SMART PARSING ---
            # We try to treat the output as the structured Dict we sent.
            try:
                # If the SDK passed it as a stringified dict/json
                parsed = json.loads(raw_output)
                
                if isinstance(parsed, dict) and parsed.get("status") == "success":
                    content = parsed.get("content", "")
                    print(f" [SUCCESS] {url} | length={len(content)}")
                    return (url, content)
                
                elif isinstance(parsed, dict) and parsed.get("status") == "error":
                    msg = parsed.get("message", "Unknown tool error")
                    print(f" [TOOL ERROR] {url}: {msg}")
                    return (url, f"Tool error: {msg}")

            except (json.JSONDecodeError, TypeError):
                # If it's not JSON, it means the SDK/Tool returned the raw text 
                # directly (this often happens in simplified MCP implementations).
                print(f" [DIRECT TEXT] {url} received raw text (length={len(raw_output)})")
                return (url, raw_output)

            return (url, raw_output)

        except Exception as e:
            print(f" [SCRAPE TASK ERROR] {url}: {str(e)}")
            return (url, f"Error extracting {url}: {str(e)}")

    try:
        await client.connect()

        print(f"\n--- DEBUG: Extracting {len(urls_to_scrape)} URLs in parallel ---")

        # Run all scraping tasks concurrently
        results = await asyncio.gather(*(scrape_task(u) for u in urls_to_scrape))

        print("\n [EXTRACTION RESULTS SUMMARY]")
        for url, text in results:
            print(f"--- {url} ---")
            print(f"Length: {len(text)}")
            print(f"Preview: {text[:100]}...\n")

        extracted_data = {url: text for url, text in results}

        return {
            "content_store": extracted_data,
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