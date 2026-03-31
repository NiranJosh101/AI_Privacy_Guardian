import asyncio
import json
from typing import Dict, Any
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient


async def extraction_node(state: ExplorerState) -> Dict[str, Any]:
    regulatory_map = state.get("regulatory_map", {})
    urls_to_scrape = set()

    # Extract URLs
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

            content_list = getattr(response, "content", [])

            if content_list and len(content_list) > 0:
                #  FIX: get actual first item
                first_item = content_list[0]

                print(f" [RAW MCP ITEM] {url}: {first_item}")

                # Extract text safely
                if hasattr(first_item, "text"):
                    raw_text = first_item.text
                else:
                    raw_text = str(first_item)

                print(f" [RAW TEXT LENGTH] {url}: {len(raw_text)}")

                #  Parse JSON response from MCP tool
                try:
                    parsed = json.loads(raw_text)

                    if parsed.get("status") == "success":
                        content = parsed.get("content", "")
                        print(f" [PARSED CONTENT] {url} | length={len(content)}")
                        print(f" [PREVIEW] {content[:200]}")
                        return (url, content)

                    else:
                        msg = parsed.get("message", "Unknown error")
                        print(f" [TOOL ERROR] {url}: {msg}")
                        return (url, f"Tool error: {msg}")

                except json.JSONDecodeError:
                    print(f"⚠️ [JSON PARSE FAILED] {url}, returning raw text")
                    return (url, raw_text)

            print(f"❌ [EMPTY MCP RESPONSE] {url}")
            return (url, f"Empty content returned for {url}")

        except Exception as e:
            print(f" [SCRAPE TASK ERROR] {url}: {str(e)}")
            return (url, f"Error extracting {url}: {str(e)}")

    try:
        await client.connect()

        print(f"\n--- DEBUG: Extracting {len(urls_to_scrape)} URLs in parallel ---")

        results = await asyncio.gather(*(scrape_task(u) for u in urls_to_scrape))

        print("\n [EXTRACTION RESULTS SUMMARY]")
        for url, text in results:
            print(f"--- {url} ---")
            print(f"Length: {len(text)}")
            print(f"Preview: {text[:150]}\n")

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