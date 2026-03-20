# app/mcp/tools/validator.py

import time
import httpx
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()


class SiteValidator:
    """
    A robust pre-crawl validator that checks:
    - Accessibility
    - Bot blocking
    - CAPTCHA presence
    - JS requirements
    """

    def __init__(self):
        self.timeout = 10.0
        self.max_retries = 2

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

        self.block_indicators = [
            "captcha",
            "access denied",
            "forbidden",
            "verify you are human",
            "cloudflare",
            "blocked",
            "bot detection",
        ]

        self.min_content_length = 500  # threshold for "empty" pages

    def _detect_blocks(self, content: str, status_code: int) -> Dict[str, Any]:
        """
        Analyze response content for blocking signals.
        """
        content_lower = content.lower()

        has_block_keywords = any(k in content_lower for k in self.block_indicators)

        has_captcha = "captcha" in content_lower

        js_required = (
            "enable javascript" in content_lower
            or "please turn on javascript" in content_lower
        )

        is_empty = len(content_lower.strip()) < self.min_content_length

        is_blocked_status = status_code in [403, 429, 503]

        return {
            "is_blocked": is_blocked_status or has_block_keywords,
            "has_captcha": has_captcha,
            "js_required": js_required,
            "is_empty": is_empty,
            "block_detected": has_block_keywords,
            "status_block": is_blocked_status,
        }

    async def validate(self, url: str) -> Dict[str, Any]:
        """
        Main validation logic with retries and diagnostics.
        """
        last_error: Optional[str] = None

        async with httpx.AsyncClient(
            headers=self.headers,
            follow_redirects=True,
            timeout=self.timeout,
        ) as client:

            for attempt in range(self.max_retries):
                try:
                    start_time = time.time()

                    response = await client.get(url)

                    elapsed = time.time() - start_time

                    content = response.text

                    signals = self._detect_blocks(content, response.status_code)

                    redirected = len(response.history) > 0

                    can_proceed = (
                        response.status_code == 200
                        and not signals["is_blocked"]
                        and not signals["is_empty"]
                    )

                    return {
                        "status_code": response.status_code,
                        "final_url": str(response.url),
                        "redirected": redirected,
                        "redirect_chain": [str(r.url) for r in response.history],

                        "response_time": round(elapsed, 2),

                        "can_proceed": can_proceed,

                        # Signals
                        **signals,
                    }

                except Exception as e:
                    last_error = str(e)

        return {
            "can_proceed": False,
            "error": last_error,
        }


# MCP Tool Wrapper
@mcp.tool()
async def validate_site_access(url: str) -> Dict[str, Any]:
    """
    Validates if a site is accessible and safe to crawl.
    """
    validator = SiteValidator()
    return await validator.validate(url)