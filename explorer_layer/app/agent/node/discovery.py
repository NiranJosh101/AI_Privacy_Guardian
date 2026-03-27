import json
import logging
from typing import Dict, Any, List
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

# Set up logging for better observability in the agent loop
logger = logging.getLogger(__name__)

async def discovery_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Calls the MCP 'discover_regulatory_links' tool.
    Robustly handles MCP content wrapping and JSON parsing.
    """
    client = MCPClient()
    base_url = state.get("base_url")
    
    # Initialize default return values to keep State consistent
    update = {
        "regulatory_map": {},
        "is_blocked": False,
        "error_log": state.get("error_log", [])
    }

    if not base_url:
        logger.error("No base_url found in state.")
        update["is_blocked"] = True
        return update

    try:
        await client.connect()
        
        response = await client.call_tool(
            "discover_regulatory_links", 
            {"url": base_url}
        )
        
        # 1. Access the content list correctly
        content_items = getattr(response, 'content', [])
        if not content_items:
            logger.warning(f"MCP tool returned empty content for {base_url}")
            return update

        # 2. Extract the first item (MCP tools usually return one primary result)
        first_item = content_items
        raw_data = None

        # 3. Robust Type-Checking for MCP Content
        # Check if it's an MCP TextContent object (has .text)
        if hasattr(first_item, "text"):
            raw_data = first_item.text
        # Check if it's a raw dictionary (already parsed by the client)
        elif isinstance(first_item, dict):
            # If the tool returned a dict, but it's wrapped in a 'text' key inside that dict
            raw_data = first_item.get("text", first_item)
        else:
            # Fallback for unexpected string representations
            raw_data = str(first_item)

        # 4. Final JSON parsing if the data is still a string
        if isinstance(raw_data, str):
            try:
                update["regulatory_map"] = json.loads(raw_data)
            except json.JSONDecodeError:
                # Sometimes tools return a string that isn't JSON; handle gracefully
                logger.error(f"Failed to parse JSON from tool: {raw_data[:100]}")
                update["error_log"].append("Tool returned invalid JSON format")
        else:
            update["regulatory_map"] = raw_data

    except Exception as e:
        error_msg = f"Discovery node failed for {base_url}: {str(e)}"
        logger.exception(error_msg)
        update["is_blocked"] = True
        update["error_log"].append(error_msg)
        
    finally:
        # Crucial: Always close connection to prevent resource leaks
        try:
            await client.disconnect()
        except Exception:
            pass

    return update