import asyncio
import logging
from typing import Optional, Any, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class MCPClient:
    """
    The 'Hand' that reaches into the Toolbox (MCP Server).
    Fixed: Properly returns full MCP response instead of just content.
    """

    def __init__(self, url: str = "http://localhost:8002/sse"):
        self.url = url
        self.session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        """Initialize SSE connection and MCP session."""
        try:
            logger.debug(f"Connecting to MCP Server at {self.url}")

            streams = await self._exit_stack.enter_async_context(
                sse_client(self.url)
            )
            read_stream, write_stream = streams

            self.session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            await self.session.initialize()
            logger.debug("MCP Handshake Complete")

        except Exception as e:
            await self.disconnect()
            logger.exception(f"Connection Failed: {e}")
            raise

    async def get_available_tools(self):
        if not self.session:
            raise RuntimeError("MCP Client not connected.")

        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executes a tool and returns FULL response (not just content).
        """
        if not self.session:
            raise RuntimeError("MCP Client not connected.")

        try:
            logger.debug(f"Calling tool: {tool_name} with args: {arguments}")

            result = await self.session.call_tool(tool_name, arguments)

            # 🔍 Deep debug (this is gold when things break)
            logger.debug(f"MCP RAW RESULT: {result}")
            logger.debug(f"MCP RESULT CONTENT: {getattr(result, 'content', None)}")

            return result  # ✅ CRITICAL FIX

        except Exception as e:
            logger.exception(f"Tool call failed: {tool_name} | Error: {e}")
            raise

    async def disconnect(self):
        """Gracefully shut down connection."""
        logger.debug("Disconnecting MCP Client")

        try:
            await self._exit_stack.aclose()
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

        self.session = None