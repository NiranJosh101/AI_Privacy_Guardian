# app/agent/nodes/validation_node.py

import json
import asyncio
import logging
from langsmith import traceable
from typing import Dict, Any, Optional
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

logger = logging.getLogger(__name__)



_client: Optional[MCPClient] = None
_client_lock = asyncio.Lock()

@traceable(name="Validation Node", run_type="chain")
async def _get_client() -> MCPClient:
    """
    Return the shared MCPClient, creating and connecting it on first call.
    Thread-safe via asyncio.Lock — safe for concurrent LangGraph node calls.
    """
    global _client
    async with _client_lock:
        if _client is None:
            logger.info("[mcp_singleton] Creating new MCPClient and connecting...")
            instance = MCPClient()
            await instance.connect()
            _client = instance
            logger.info("[mcp_singleton] MCPClient connected and ready.")
    return _client


async def _invalidate_client() -> None:
    """
    Clear the singleton after a transport-level failure.
    Attempts a graceful disconnect first so the server isn't left hanging.
    The next call to _get_client() will create a fresh connection.
    """
    global _client
    async with _client_lock:
        if _client is not None:
            logger.warning("[mcp_singleton] Invalidating client due to failure.")
            try:
                await _client.disconnect()
            except Exception:
                pass  # Already broken — we just want the exit_stack cleaned up
            _client = None


async def _call_with_retry(tool_name: str, arguments: Dict[str, Any], timeout: float) -> Any:
    """
    Call an MCP tool with a timeout, retrying once on transport failure.

    WHY ONE RETRY:
      SSE connections can drop silently between agent runs (server restart,
      network hiccup, idle timeout). The first failure invalidates the broken
      singleton. The retry gets a fresh connection. If it fails again, that's
      a real error and we let it propagate.

    WHY NOT INFINITE RETRIES:
      We don't want to mask a broken MCP server by looping forever. One retry
      is enough to recover from a stale connection. Anything beyond that is a
      real infrastructure problem that should surface as an error.
    """
    for attempt in range(2):  # attempt 0 = first try, attempt 1 = one retry
        client = await _get_client()
        try:
            return await asyncio.wait_for(
                client.call_tool(tool_name, arguments),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            # Timeout is not a transport failure — don't retry, surface it.
            raise RuntimeError(
                f"MCP tool '{tool_name}' timed out after {timeout}s"
            )
        except Exception as exc:
            if attempt == 0:
                # First failure — could be a stale SSE connection.
                # Invalidate and let the loop retry with a fresh one.
                logger.warning(
                    f"[mcp_retry] Tool call failed on attempt {attempt + 1}, "
                    f"reconnecting. Error: {exc}"
                )
                await _invalidate_client()
                continue
            # Second failure — this is a real error.
            raise




def _parse_response(response: Any) -> Dict[str, Any]:
    """
    Normalise a CallToolResult into a plain Python dict.

    Handles:
      - content[0] is already a dict       (some MCP server implementations)
      - content[0] has a .text attribute   (standard MCP TextContent object)
      - content[0] is a raw JSON string    (less common but seen in practice)

    Raises ValueError with a clear message on anything unexpected so the
    caller gets an actionable error rather than a silent KeyError.
    """
    content_list = getattr(response, "content", response)

    if not isinstance(content_list, list) or not content_list:
        raise ValueError(
            f"Expected non-empty list in MCP response, got: {type(content_list)}"
        )

    first = content_list[0]

    if isinstance(first, dict):
        return first

    if hasattr(first, "text"):
        try:
            return json.loads(first.text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"MCP TextContent.text is not valid JSON — got: {first.text!r}"
            ) from exc

    if isinstance(first, str):
        try:
            return json.loads(first)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"MCP string content is not valid JSON — got: {first!r}"
            ) from exc

    raise ValueError(
        f"Unrecognised MCP content item type: {type(first)}"
    )


TOOL_TIMEOUT = 15.0


@traceable(name="Validation Node", run_type="chain")
async def validation_node(state: ExplorerState) -> Dict[str, Any]:
    """
    The Gatekeeper. Checks if the target URL is healthy and accessible
    before committing to the expensive discovery and extraction pipeline.

    State patches returned:
      Success → { base_url, is_blocked: False, current_step: "validated" }
      Failure → { is_blocked: True, error_log: [reason] }
    """
    url = state["base_url"]
    logger.info(f"[validation_node] Starting — url={url}")

    try:
        response = await _call_with_retry(
            tool_name="validate_site_access",
            arguments={"url": url},
            timeout=TOOL_TIMEOUT,
        )

        result = _parse_response(response)

        # Log validation_method so LangSmith traces show fast_path vs browser_path
        method = result.get("validation_method", "unknown")
        response_time = result.get("response_time", "?")
        logger.debug(
            f"[validation_node] Result received — method={method}, "
            f"response_time={response_time}s, can_proceed={result.get('can_proceed')}"
        )

        if not result.get("can_proceed", False):
            reason = result.get("error", "Site blocked or inaccessible")
            logger.warning(f"[validation_node] Blocked — {url} — {reason}")
            return {
                "is_blocked": True,
                "error_log": [f"Site Validation Failed: {reason}"],
            }

        final_url = result.get("final_url", url)
        logger.info(
            f"[validation_node] OK — method={method}, time={response_time}s, "
            f"final_url={final_url}"
        )
        return {
            "base_url": final_url,
            "is_blocked": False,
            "current_step": "validated",
        }

    except Exception as exc:
        logger.error(f"[validation_node] Fatal error — {exc}", exc_info=True)
        return {
            "is_blocked": True,
            "error_log": [f"Validator Node Error: {exc}"],
        }