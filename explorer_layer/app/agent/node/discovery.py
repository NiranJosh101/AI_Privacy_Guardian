import json
import logging
from typing import Dict, Any

from langsmith import traceable

from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

logger = logging.getLogger(__name__)


def extract_mcp_text_content(response) -> str:
    """
    Safely extracts the first valid text payload from an MCP response.
    Raises ValueError if no valid text content is found.
    """
    content_items = getattr(response, "content", [])

    if not content_items:
        raise ValueError("MCP response has no content")

    for item in content_items:
        # Case 1: TextContent object
        if hasattr(item, "text") and isinstance(item.text, str) and item.text.strip():
            return item.text

        # Case 2: dict-like structure
        if isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                return text

        # Case 3: raw string (rare fallback, but valid)
        if isinstance(item, str) and item.strip().startswith("{"):
            return item

    raise ValueError(f"No valid text payload found in MCP response: {content_items}")

@traceable(name="Discovery Node", run_type="chain")
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
        update["is_blocked"] = True
        update["error_log"].append("No base_url provided")
        return update

    try:
        await client.connect()

        # 1. Call MCP tool
        response = await client.call_tool(
            "discover_regulatory_links",
            {"url": base_url}
        )

        # 2. Extract clean text payload (FIXED CORE ISSUE)
        try:
            raw_payload = extract_mcp_text_content(response)
        except ValueError as e:
            logger.error(f"Discovery Node: {str(e)}")
            update["is_blocked"] = True
            update["error_log"].append(str(e))
            return update

        # 3. Parse JSON safely
        try:
            parsed_data = json.loads(raw_payload)
        except json.JSONDecodeError:
            logger.error(f"Discovery Node: Failed to parse JSON: {raw_payload[:200]}")
            update["is_blocked"] = True
            update["error_log"].append("Malformed JSON from tool")
            return update

        # 4. Extract fields
        status = parsed_data.get("status")
        categories_found = parsed_data.get("categories", {})

        if status == "error":
            message = parsed_data.get("message", "Internal tool error")
            logger.error(f"Discovery Node: Tool error: {message}")
            update["is_blocked"] = True
            update["error_log"].append(message)

        elif status == "no_links_found" or not categories_found:
            logger.info(f"Discovery Node: No regulatory links for {base_url}")
            update["regulatory_map"] = {}

        else:
            logger.info(
                f"Discovery Node: Success. {len(categories_found)} categories mapped."
            )
            update["regulatory_map"] = categories_found

    except Exception as e:
        logger.exception(f"Discovery Node: Unexpected failure: {str(e)}")
        update["is_blocked"] = True
        update["error_log"].append(f"Node Exception: {str(e)}")

    finally:
        try:
            await client.disconnect()
        except Exception:
            pass

    print(f"--- DISCOVERY COMPLETE: {len(update['regulatory_map'])} categories found ---")
    return update