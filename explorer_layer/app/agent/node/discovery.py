import json
import logging
from typing import Dict, Any

from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

logger = logging.getLogger(__name__)

async def discovery_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Calls the MCP 'discover_regulatory_links' tool and unwraps the nested 
    'categories' results into the agent state.
    """
    client = MCPClient()
    base_url = state.get("base_url")

    update = {
        "regulatory_map": {},
        "is_blocked": False,
        "error_log": state.get("error_log", []),
    }

    if not base_url:
        logger.error("Discovery Node: No base_url provided in state.")
        return update

    try:
        await client.connect()
        
        # 1. Call the tool
        response = await client.call_tool("discover_regulatory_links", {"url": base_url})

        # 2. Get the content list from the MCP CallToolResult
        content_items = getattr(response, "content", [])
        if not content_items:
            logger.warning(f"Discovery Node: MCP returned empty content for {base_url}")
            update["is_blocked"] = True
            update["error_log"].append("Tool returned no content")
            return update

        # --- CRITICAL FIX ---
        # content_items is a LIST. We must grab the first element.
        first_content_block = content_items[0]
        
        raw_payload = None

        # Check if it's a TextContent object (has .text attribute)
        if hasattr(first_content_block, "text"):
            raw_payload = first_content_block.text


        # Check if it's a dictionary (standard JSON return)
        elif isinstance(first_content_block, dict):
            raw_payload = first_content_block.get("text", first_content_block)
     
        else:
            raw_payload = str(first_content_block)
        # --- END FIX ---

        if not raw_payload:
            update["is_blocked"] = True
            update["error_log"].append("Empty payload from tool")
            return update

        raw_payload = raw_payload.strip()

        # 4. Safe JSON Parsing
        if isinstance(raw_payload, str):
            try:
                parsed_data = json.loads(raw_payload)
            except json.JSONDecodeError:
                logger.error(f"Discovery Node: Failed to parse JSON: {raw_payload[:100]}")
                update["is_blocked"] = True
                update["error_log"].append("Malformed JSON from tool")
                return update
        else:
            parsed_data = raw_payload

        # 5. Unwrap the 'LinkScout' wrapper structure
        status = parsed_data.get("status")
        categories = parsed_data.get("categories", {})

        if status == "error":
            logger.error(f"Discovery Node: Tool reported error: {parsed_data.get('message')}")
            update["is_blocked"] = True
            update["error_log"].append(parsed_data.get("message", "Internal tool error"))
        elif status == "no_links_found":
            logger.info(f"Discovery Node: No links matched categories for {base_url}")
            update["regulatory_map"] = {} 
        else:
            logger.info(f"Discovery Node: Successfully retrieved {len(categories)} categories")
            update["regulatory_map"] = categories

    except Exception as e:
        logger.exception(f"Discovery Node: Unexpected failure: {str(e)}")
        update["is_blocked"] = True
        update["error_log"].append(f"Node Exception: {str(e)}")
    finally:
        try:
            await client.disconnect()
        except:
            pass

    return update